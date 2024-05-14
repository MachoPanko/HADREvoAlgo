# This is a sample Python script.
import tents
import numpy as np
import maps


def possible_solution(tents_requested, entrance_xy, xy_out_of_bounds, area_length, area_breadth):
    global tents
    area_length = area_length
    area_breadth = area_breadth
    area_given = area_length * area_breadth
    estimated_minarea_required = 0

    ####

    placing_order_init = ["SentryTent"]
    tents_requested_init = []
    for tent in tents_requested:
        if tent.__class__.__name__ in placing_order_init:
            tents_requested_init.append(tent)

    ####
    ####
    placing_order_dirty = ["LogisticsTent", "MaintenanceTent", "POLTent", "EnsuiteDuoTent", "CleanTent"]
    tents_requested_dirty = []
    for tent in tents_requested:
        if tent.__class__.__name__ in placing_order_dirty:
            tents_requested_dirty.append(tent)

    tents_area_dirty = 0
    for tents in tents_requested_dirty:
        tents_area_dirty += tents.length * tents.breadth
    ####
    ####
    placing_order_clean_operations = ["UCCTent", "MedicalTent"]
    tents_requested_clean_operations = []
    for tent in tents_requested:
        if tent.__class__.__name__ in placing_order_clean_operations:
            tents_requested_clean_operations.append(tent)

    tents_area_clean_operations = 0
    for tents in tents_requested_clean_operations:
        tents_area_clean_operations += tents.length * tents.breadth
    ####
    ####
    placing_order_clean_admin = ["CommunityTent", "MessTent", "RestTent", "K9Tent"]
    tents_requested_clean_admin = []
    for tent in tents_requested:
        if tent.__class__.__name__ in placing_order_clean_admin:
            tents_requested_clean_admin.append(tent)

    tents_area_clean_admin = 0
    for tents in tents_requested_clean_admin:
        tents_area_clean_admin += tents.length * tents.breadth
    ####

    # tents_area_total = tents_area_clean_admin + tents_area_clean_operations + tents_area_dirty
    # tents_percentage_dirty = tents_area_dirty / tents_area_total
    # tents_percentage_clean_operations = tents_area_clean_operations / tents_area_total
    # tents_percentage_clean_admin = tents_area_clean_admin / tents_area_total
    #
    # print(tents_percentage_clean_admin, tents_percentage_clean_operations, tents_percentage_dirty)
    # placing_order = ["SentryTent", "LogisticsTent", "CommunityTent" , "MaintenanceTent", "POLTent", "UCCTent", "EnsuiteDuoTent", "MedicalTent", "MessTent", "RestTent", "K9Tent", "CleanTent"]
    # xy_out_of_bounds =[]
    ret_tent_list = []
    ret_zones = []

    for tent in tents_requested:
        estimated_minarea_required += tent.length * tent.breadth
    if estimated_minarea_required < area_given:
        # print("number of tents: " + str(len(tents_requested)))

        mapy_init = maps.Map(area_length, area_breadth, tents_requested_init, entrance_xy, xy_out_of_bounds,
                             placing_order=placing_order_init, tentList_full=tents_requested)
        mapy_init = mapy_init.CSP()[1]
        ret_tent_list.extend(mapy_init.btm_left_xy)
        ret_zones.append(mapy_init.topleftbottomright)
        ####
        mapy_dirty = maps.Map(area_length, area_breadth, tents_requested_dirty, entrance_xy, xy_out_of_bounds,
                              placing_order=placing_order_dirty, tentList_full=tents_requested)
        mapy_dirty.matrix_traversal_choice , mapy_dirty.length_traversal, mapy_dirty.breadth_traversal = mapy_init.matrix_traversal_choice , mapy_init.length_traversal, mapy_init.breadth_traversal
        mapy_dirty.matrix = mapy_init.matrix
        mapy_dirty.update_clusters(mapy_init)
        mapy_dirty = mapy_dirty.CSP()[1]
        ret_tent_list.extend(mapy_dirty.btm_left_xy)
        ret_zones.append(mapy_dirty.topleftbottomright)
        # input()
        ####
        mapy_clean_operations = maps.Map(area_length, area_breadth, tents_requested_clean_operations, entrance_xy,
                                         xy_out_of_bounds, placing_order=placing_order_clean_operations, tentList_full=tents_requested)
        mapy_clean_operations.matrix_traversal_choice, mapy_clean_operations.length_traversal, mapy_clean_operations.breadth_traversal = mapy_dirty.matrix_traversal_choice, mapy_dirty.length_traversal, mapy_dirty.breadth_traversal
        mapy_clean_operations.matrix = mapy_dirty.matrix
        mapy_clean_operations.update_clusters(mapy_dirty)
        mapy_clean_operations = mapy_clean_operations.CSP()[1]
        ret_tent_list.extend(mapy_clean_operations.btm_left_xy)
        ret_zones.append(mapy_clean_operations.topleftbottomright)
        # input()
        ####
        mapy_clean_admin = maps.Map(area_length, area_breadth, tents_requested_clean_admin, entrance_xy,
                                    xy_out_of_bounds,
                                    placing_order=placing_order_clean_admin, tentList_full=tents_requested)
        mapy_clean_admin.matrix_traversal_choice, mapy_clean_admin.length_traversal, mapy_clean_admin.breadth_traversal = mapy_clean_operations.matrix_traversal_choice, mapy_clean_operations.length_traversal, mapy_clean_operations.breadth_traversal
        mapy_clean_admin.matrix = mapy_clean_operations.matrix
        mapy_clean_admin.update_clusters(mapy_clean_operations)
        mapy_clean_admin = mapy_clean_admin.CSP()[1]
        ret_tent_list.extend(mapy_clean_admin.btm_left_xy)
        ret_zones.append(mapy_clean_admin.topleftbottomright)
        # print("here")
        # print("mapyclean",mapy_clean_admin.btm_left_xy)
        # print(ret_tent_list)
        # print(ret_zones)
        mapy_clean_admin.btm_left_xy = ret_tent_list
        mapy_clean_admin.zones = ret_zones
        ##
        ## TENT LIST AND COORDINATES
        # print("ret_tent")
        # print(ret_tent_list)
        # print(len(ret_tent_list))
        ## ZONE XYXY from top left to bottom right
        # print(ret_zones)
        # print("debug")
        # for row in mapy_clean_admin.printable():
        #     print(row)
        return mapy_clean_admin, ret_zones, ret_tent_list
    else:
        print("Not enough space!")
        return None, ret_zones, ret_tent_list
