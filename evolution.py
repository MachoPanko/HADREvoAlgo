import copy
import numpy
import csp
import maps
import random
from time import perf_counter
import tents


## Evo Algo Parameters
def EvoAlgo(tents_requested, entrance_xy, xy_out_of_bounds, area_length=50, area_breadth=32, population_size=30):

    population_size = 10
    population = []
    best_fitness = -9999
    best_map = 0
    ## Init Evo Population
    for i in range(population_size):
        legal_solution, zones, tentlist = csp.possible_solution(tents_requested, entrance_xy, xy_out_of_bounds,
                                                                area_length, area_breadth)
        # for row in legal_solution.printable():
        #     print(row)
        # print("before:",legal_solution.btm_left_xy)
        # print("after:", tentlist)

        legal_solution.clear_oob_markers()
        legal_solution.place_oob_markers()
        legal_solution.heuristic_matrix = [[set() for _ in range(legal_solution.breadth)] for _ in
                                           range(legal_solution.length)]
        # print("after reset: ", legal_solution.btm_left_xy)
        legal_solution.update_choice_matrix()
        # print("done")
        # legal_solution.btm_left_xy = tentlist
        population.append(legal_solution)
        # print("after after: ", legal_solution.btm_left_xy)
        print("initial fitness", fitness(population[i]))

    # print("len_og ", len(tents_requested))
    # for row in population[0].printable():
    #     print(row)
    # input("ada")
    # print("OMG????")
    # for row in population[0].choices_matrix:
    #     print(row)
    # initial_xy = copy.deepcopy(population[0].btm_left_xy)
    ##debug 1
    # for row in population[0].printable():
    #     print(row)
    # #
    print("Mess Cluster: ", population[0].messCluster)
    print("Decon Cluster: ", population[0].cleanCluster)
    print("Medical Cluster: ", population[0].medicalCluster)

    # print(len(population[0].choices_matrix), len(population[0].choices_matrix[0]))

    start_time = perf_counter()
    end_time = perf_counter()
    # mutate_3ps(population[0], random.randint(1, 3), random.randint(1, 2))
    while end_time - start_time < 5: ## Temporary Terminating condition is just a loop
        # print("btm",population[0].btm_left_xy)
        prev_population = copy.deepcopy(population)

        ## Mutate
        for i in range(len(population)):
            # print("before")
            # for row in population[i].choices_matrix:
            #     print(row)
            mutate_3ps(population[i])
            fitness_of_map = fitness(population[i])
            print()
            print("current fitness", fitness_of_map)
            # for row in population[i].printable():
            #     print(row)
            # print("after")
            # for row in population[i].choices_matrix:
            #     print(row)
            if(fitness_of_map > best_fitness):
                best_fitness = fitness_of_map
                print("new best",best_fitness)
                best_map = population[i]

        ## Add previous Populace
        population.extend(prev_population)
        populace_fitness = []
        ## Survivor Selection
        # Find fitness for populace

        for p in population:
            populace_fitness.append(fitness(p))
        # Sort population according to fitness

        population_1 = numpy.array(population)
        fitness_1 = numpy.array(populace_fitness)
        inds = fitness_1.argsort()
        fitness_1 = numpy.sort(fitness_1)[::-1].tolist()
        population_1 = population_1[inds]
        population = population_1[::-1].tolist()
        # Tournament selection
        # population = elitist_tournament_selection(population_1, fitness_1 , 0 , int(0.4*population_size), population_size)
        population = population[:population_size]
        # print(fitness_1)
        # Update time for terminating condition
        end_time = perf_counter()


    print("best",best_fitness)
    for row in best_map.printable():
        print(row)


    print("Mess Cluster: ", population[0].messCluster)
    print("Decon Cluster: ", population[0].cleanCluster)
    print("Medical Cluster: ", population[0].medicalCluster)




def fitness(mapy):
    score = 0
    ## for more rentangular clusters
    for coords,cluster_names in mapy.cluster_top_left_btm_right():
        top = coords[0]
        left = coords[1]
        bottom = coords[2]
        right = coords[3]
        for row in range(top,bottom+1):
            for col in range(left,right+1):
                current_point = mapy.matrix[row][col]
                if type(current_point) != int and current_point.tent_type in cluster_names:
                    score += 1
                else:
                    score -= 1
    return score

def num_connections(point, mapy):
    point_row = point[0]
    point_col = point[1]
    tent =  mapy.matrix[point_row][point_col]
    tent_type = tent.tent_type
    connections = 0

    if point_row - tent.length - tent.spacing > 0 and type(mapy.matrix[point_row - tent.length - tent.spacing][point_col]) == type(tent):
        connections += 1
    if point_row + tent.length + tent.spacing < mapy.length and type(mapy.matrix[point_row + tent.length + tent.spacing][point_col]) ==  type(tent):
        connections += 1
    if point_col- tent.breadth - tent.spacing > 0 and type(mapy.matrix[point_row][point_col- tent.breadth - tent.spacing]) ==  type(tent):
        connections += 1
    if point_col+ tent.breadth + tent.spacing < mapy.breadth and type(mapy.matrix[point_row][point_col+ tent.breadth + tent.spacing]) ==  type(tent):
        connections += 1
    return connections

def elitist_tournament_selection(population, fitness_scores, num_elite, tournament_size, desired_population_size):
    """
    Performs elitist tournament selection.

    Args:
        population (list): List of individuals (genomes).
        fitness_scores (list): List of fitness scores corresponding to each individual.
        num_elite (int): Number of elite individuals to preserve.
        tournament_size (int): Size of each tournament.

    Returns:
        list: List of selected elite individuals.
    """

    elite_individuals = [population[i] for i in range(num_elite)]

    # Fill the remaining slots using tournament selection
    remaining_slots = desired_population_size - num_elite
    for _ in range(remaining_slots):
        tournament_indices = random.sample(range(len(population)), tournament_size)
        print("infices",tournament_indices)
        print("fits", fitness_scores)

        winner_index = max(tournament_indices, key=lambda i: fitness_scores[i])
        print("winner",winner_index)
        print(fitness_scores[winner_index])
        elite_individuals.append(population[winner_index])

    return elite_individuals

def random_eligible_point(mapy):
    point = random.choice(mapy.btm_left_xy)
    point_row = point[0]
    point_col = point[1]
    tent =  mapy.matrix[point_row][point_col]
    if not issubclass(type(tent), tents.BigClusterTent):
        return point
    ## if is cluster tent
    cluster = tent.getCluster(mapy)
    min_connections = 999
    for point in cluster:

        current_connections = num_connections(point,mapy)
        if current_connections < min_connections:
            min_connections = current_connections
            point_with_min_connections = copy.deepcopy(point)
    point_with_min_connections.extend([tent.tent_type])
    # print(point_with_min_connections)
    return point_with_min_connections



def mutate_3ps(mapy, points_to_swap=3,repetitions=2):  # stands for 3 point swap ##eh tao in the case of no 3ps avail the system will get stuck in while loop, pls take care of this
    points_used = []
    choices_used = []
    ## if its lesser than 3, the while loop will loop forever
    if mapy.number_of_choices() < 3:
        return
    ##Number of 3PS done

    for repetition in range(repetitions):
        for rep in range(points_to_swap):
            # print(mapy.restCluster, 0)
            point = random_eligible_point(mapy) ## in process of CHANGing BUG HERE because this will cause split clusters (disconnected clusters)
            # print(mapy.restCluster, 3)
            choices = mapy.choices_for_tent(point[0], point[1], point[2])
            # print(mapy.restCluster, 0)
            if not mapy.is_choices_available(choices):
                continue
            destination = random.choice(choices)
            # print(mapy.restCluster , 1)
            while (not mapy.is_choices_available(choices)) or destination in choices_used or point in points_used:
                point = random_eligible_point(mapy)
                choices = mapy.choices_for_tent(point[0], point[1],point[2])

                if not mapy.is_choices_available(choices):
                    continue
                destination = random.choice(choices)

            points_used.append(point)
            choices_used.append(destination)
            # print( "points", points_used)
            # print("choices",choices_used)
            ## bro uncomment this you can visibly see sometimes it might not end well, erm this should be improved after intial trials cuz i believe this will really boost performance
            # print(destination)
            # print(point)
            ## start mutating

            row_source = point[0]
            col_source = point[1]

            row_destination = destination[0]
            col_destination = destination[1]
            source_tent = mapy.matrix[row_source][col_source]
            # for row in mapy.printable():
            #     print(row)
            # print(row_source, col_source)
            source_tent.unplace2(row_source, col_source, mapy)
            source_tent.place2(row_destination, col_destination, mapy)

            mapy.update_choice_matrix()

def sort_list_given_index(list1, list2):

    zipped_pairs = zip(list2, list1)

    z = [x for _, x in sorted(zipped_pairs)]

    return z

