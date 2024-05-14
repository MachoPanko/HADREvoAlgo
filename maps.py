import copy
import math
import random
import tents
import numpy as np
import inspect
import sys


# placing_order = ["SentryTent", "LogisticsTent", "MaintenanceTent", "POLTent", "EnsuiteDuoTent", "CleanTent", "UCCTent",  "CommunityTent", "MedicalTent", "MessTent", "RestTent", "K9Tent"]
class Map:
    def __init__(self, length, breadth, tentList, entrance_xy, xy_out_of_bounds, placing_order, tentList_full):
        self.btm_left_xy = []
        self.zones = []
        self.entrance_xy = entrance_xy
        self.xy_out_of_bounds = xy_out_of_bounds
        self.length = length
        self.breadth = breadth
        self.matrix = np.zeros((length, breadth)).astype(int).tolist()
        self.heuristic_matrix = [[set() for _ in range(self.breadth)] for _ in range(self.length)]
        self.messCluster = []
        self.MainPOLCluster = []
        self.cleanCluster = []
        self.medicalCluster = []
        self.restCluster = []
        self.ensuiteCluster = []
        self.K9Cluster = []
        self.placing_order = placing_order
        self.topleftbottomright = []
        self.choices_matrix = np.zeros((length, breadth)).astype(int).tolist()
        self.tentList_full = tentList_full
        self.tentList = tentList
        self.uniqueTents = [cls_name for cls_name, cls_obj in inspect.getmembers(sys.modules['tents']) if
                            inspect.isclass(cls_obj)]
        self.matrix_traversal_choice = [[self.length - 1, -1, -1], [self.breadth - 1, -1, -1]]
        # self.matrix_traversal_choice = [[0, self.length, 1], [0, self.breadth, 1]]
        # self.matrix_traversal_choice = random.choice([[[self.length - 1, -1, -1], [self.breadth - 1, -1, -1]],
        #                                               [[0, self.length, 1], [0, self.breadth, 1]],
        #                                               [[0, self.length, 1], [self.breadth - 1, -1, -1]],
        #                                               [[self.length - 1, -1, -1], [0, self.breadth, 1]]])
        self.length_traversal = range(self.matrix_traversal_choice[0][0], self.matrix_traversal_choice[0][1],
                                      self.matrix_traversal_choice[0][2])
        self.breadth_traversal = range(self.matrix_traversal_choice[1][0], self.matrix_traversal_choice[1][1],
                                       self.matrix_traversal_choice[1][2])
        self.tentDict = {}
        self.tentset_name = set(tent.tent_type for tent in tentList_full)
        self.tentset = []
        module = __import__("tents")
        for tent_type in self.tentset_name:
            tent_type = getattr(module, tent_type)
            instance = tent_type()
            self.tentset.append(instance)

        self.place_oob_markers()
        for tent_names in self.uniqueTents:
            self.tentDict[tent_names] = []
        for tent in self.tentList:
            self.tentDict[tent.__class__.__name__].append(tent)
    # def squash(self):

    def choices_for_tent(self,row, col, tent_type):
        choices = []
        tent = self.matrix[row][col]
        total_spacing =  tent.breadth + tent.spacing

        for i in range(self.length):
            for j in range(self.breadth):
                if i == row:
                    if j - tent.breadth - tent.spacing == col or j + tent.breadth + tent.spacing == col:
                        continue
                if j == col:
                    if i - tent.length - tent.spacing == row or i + tent.length + tent.spacing == row:
                        continue
                if tent_type in self.choices_matrix[i][j]:
                    choices.append([i, j])

        return choices

    def is_choices_available(self, choices):
        if len(choices)== 0:
            return False
        else:
            return True

    def number_of_choices(self):
        number = 0
        for row in self.choices_matrix:
            for column in row:
                number += len(column)
        return number

    def update_clusters(self, map):
        self.messCluster = map.messCluster
        self.MainPOLCluster = map.MainPOLCluster
        self.cleanCluster = map.cleanCluster
        self.medicalCluster = map.medicalCluster
        self.restCluster = map.restCluster
        self.ensuiteCluster = map.ensuiteCluster
        self.K9Cluster = map.K9Cluster

    def get_top_left_btm_right(self, array):
        top = -1
        left = -1
        bottom = -1
        right = -1
        for row,col in array:
            if top == -1 or row < top:
                top = row
            if bottom == -1 or row > bottom:
                bottom = row
            if left == -1 or col < left:
                left = col
            if right == -1 or col > right:
                right = col
        return top,left,bottom,right

    def cluster_top_left_btm_right(self):
        ret = []
        ret.append((self.get_top_left_btm_right(self.cleanCluster),("CleanTent" , "DeconTent")))
        ret.append((self.get_top_left_btm_right(self.messCluster),("MessTent")))
        ret.append((self.get_top_left_btm_right(self.medicalCluster),("MedicalTent", "IsolationTent")))
        ret.append((self.get_top_left_btm_right(self.MainPOLCluster),("MaintenanceTent", "POLTent" )))
        ret.append((self.get_top_left_btm_right(self.restCluster),("RestTent")))
        ret.append((self.get_top_left_btm_right(self.ensuiteCluster),("EnsuiteDuoTent")))
        ret.append((self.get_top_left_btm_right(self.K9Cluster),("K9Tent")))
        return ret

    def update_choice_matrix(self):
        for x in range(self.length):
            for y in range(self.breadth):
                choices = []
                for tent in self.tentset:
                    # print(x,y, tent.tent_type)
                    # print(tent.place_possible(x,y,self))and legal_matrixthing()
                    # print(1)
                    if tent.place_possible(x,y, self) and tent.is_constraints_valid(x,y,self):
                        choices.append(tent.tent_type)
                # print(x,y, choices)
                self.choices_matrix[x][y] = choices
                # input()
    def clear_oob_markers(self):
        for x in range(self.length):
            for y in range(self.breadth):
                if type(self.matrix[x][y]) == tents.OutOfBoundsMarker:
                    self.matrix[x][y] = 0
    def place_oob_markers(self):
        for xy in self.xy_out_of_bounds:
            oob = tents.OutOfBoundsMarker()
            oob.place(xy[0], xy[1], self.matrix)

    def printable(self):
        matrix = []
        for i in range(self.length):
            row = []
            for tent in self.matrix[i]:
                row.append(int(str(tent)))
            matrix.append(row)
        return matrix

    def next_map(self, tenttype):
        temp = copy.deepcopy(self)
        tent_to_remove = temp.tentDict[tenttype].pop(0)
        temp.tentList.remove(tent_to_remove)

        return temp

    def euclidean_dist(self, x_source, y_source):
        distance = (x_source - self.entrance_xy[0]) ** 2 + (y_source - self.entrance_xy[1]) ** 2
        return distance

    def clean_to_decon(self):
        min_distance = -1
        min_xy = None
        for xy in self.cleanCluster:
            distance = self.euclidean_dist(xy[0], xy[1])
            if min_distance == -1:
                min_distance = distance
                min_xy = xy
            else:
                if distance <= min_distance:
                    min_distance = distance
                    min_xy = xy

        return min_xy

    def priority_sanity_check(self, current_tent_type):
        # print(current_tent_type)
        for tent_type in self.placing_order:
            # print("in loop",tent_type)
            if tent_type == current_tent_type:
                return True
            else:
                for tent in self.tentList:
                    if tent.tent_type == tent_type:
                        return False

    def zoning(self):
        zone_radius = 4
        top = -1
        left = -1
        bottom = -1
        right = -1
        for i in self.length_traversal:
            for j in self.breadth_traversal:
                temp = self.matrix[i][j]
                if type(temp) == int:
                    continue
                if temp.tent_type in self.placing_order:
                    # if temp.id != -1 and temp.id != 15:
                    if top == -1 or i < top:
                        top = i
                    if bottom == -1 or i > bottom:
                        bottom = i
                    if left == -1 or j < left:
                        left = j
                    if right == -1 or j > right:
                        right = j

        if (top, left, bottom, right) == (-1, -1, -1, -1):
            return False
        top = max(top - zone_radius, 0)
        left = max(left - zone_radius, 0)
        bottom = min(bottom + zone_radius, self.length)
        right = min(right + zone_radius, self.breadth)
        # print(top, left, bottom, right)

        for i in range(top, bottom):
            for j in range(left, right):
                temp = self.matrix[i][j]
                if type(temp) == int:
                    tents.OutOfBoundsMarker().place(i, j, self.matrix)
        return top, left, bottom, right

    def CSP(self):

        if (len(self.tentList) == 0):
            ## Change Nearest Clean to Decon

            # result = self.clean_to_decon()
            # if result != None and type(self.matrix[result[0]][result[1]]) != tents.DeconTent:
            #     x = result[0]
            #     y = result[1]
            #     self.matrix[x][y].unplace(x, y, self)
            #     deconTent = tents.DeconTent( length=4, breadth=4)
            #     deconTent.place(x, y, self)
            self.topleftbottomright = self.zoning()
            # for row in self.printable():
            #     print(row)
            #
            # print("Mess Cluster: ", self.messCluster)
            # print("Decon Cluster: ", self.cleanCluster)
            # print("Medical Cluster: ", self.medicalCluster)
            found_solution = True

            return found_solution, self

        for tenttype in self.placing_order:
            if not self.priority_sanity_check(tenttype):
                return False,self
            for i in self.length_traversal:
                for j in self.breadth_traversal:

                    if len(self.tentDict[tenttype]) != 0:
                        # print(tenttype, i, j)
                        # if(tenttype == "MedicalTent") and  i ==8 and j == 56:
                        #     print(self.medicalCluster)
                        #     dddd("")
                        # print(self.tentDict[tenttype][0].place_possible(i, j, self))

                        if self.tentDict[tenttype][0].place_possible(i, j, self):
                            # print("possible")
                            if issubclass(self.tentDict[tenttype][0].__class__, tents.BigClusterTent):
                                self.tentDict[tenttype][0].add_to_cluster(i, j, self)

                            # self.tentDict[tenttype][0].add_to_cluster(i, j, self)
                            self.tentDict[tenttype][0].place(i, j, self)
                            tempmap = self.next_map(tenttype)
                            #
                            # for row in self.printable():
                            #     print(row)
                            #
                            # print()
                            #
                            # print(self.tentList)
                            found_solution = tempmap.CSP()
                            # Here is return once solution is found, should return a list of coords ah , as fabian requested
                            if found_solution[0]:
                                return found_solution

                            ## if come out of this recursive call, set to 0 and remove from cluster
                            self.tentDict[tenttype][0].unplace(i, j, self)

                            if issubclass(self.tentDict[tenttype][0].__class__, tents.BigClusterTent):
                                self.tentDict[tenttype][0].remove_from_cluster(i, j, self)

        return False,self
