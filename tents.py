import copy

import tents


class EmptyMarker:
    def __init__(self):
        self.length = 1
        self.breadth = 1
        self.tent_type = self.__class__.__name__
        self.id = 0

    def __str__(self):
        return str(self.id)

    def place_possible(self):
        return True

    def place(self, x, y, matrix):
        for i in range(self.length):
            for j in range(self.breadth):
                matrix[x - i][y + j] = self

    def unplace(self, x, y, matrix):
        for i in range(self.length):
            for j in range(self.breadth):
                matrix[x - i][y + j] = 0


class OutOfBoundsMarker:
    def __init__(self):
        self.length = 1
        self.breadth = 1
        self.tent_type = self.__class__.__name__
        self.id = -1

    def __str__(self):
        return str(self.id)

    def place_possible(self):
        return True

    def place(self, x, y, matrix):
        for i in range(self.length):
            for j in range(self.breadth):
                placeholder = f"{self.tent_type} {self.id}"
                # matrix[x+i][y+j] = placeholder.ljust(12)
                # print(x-i)
                #
                # print(y+j)
                matrix[x - i][y + j] = self

    def unplace(self, x, y, matrix):
        for i in range(self.length):
            for j in range(self.breadth):
                matrix[x - i][y + j] = 0


class GenericTent:

    def __init__(self, length=1, breadth=1):
        self.length = length
        self.breadth = breadth
        self.tent_type = self.__class__.__name__
        self.id = 2
        self.spacing = 1

    def __str__(self):
        return str(self.id)

    def unplace(self, x, y, map):
        map.btm_left_xy.remove([x, y, self.tent_type])
        for i in range(self.length):
            for j in range(self.breadth):
                map.matrix[x - i][y + j] = 0

    def place(self, x, y, map):
        map.btm_left_xy.append([x, y, self.tent_type])
        for i in range(self.length):
            for j in range(self.breadth):
                # placeholder = f"{self.tent_type} {self.id}"
                # matrix[x+i][y+j] = placeholder.ljust(12)
                map.matrix[x - i][y + j] = self
        map.heuristic_matrix[x][y].add(self.tent_type)

    def unplace2(self, x, y, map):
        map.btm_left_xy.remove([x, y, self.tent_type])
        for i in range(self.length):
            for j in range(self.breadth):
                map.matrix[x - i][y + j] = 0

    def place2(self, x, y, map):
        map.btm_left_xy.append([x, y, self.tent_type])
        for i in range(self.length):
            for j in range(self.breadth):
                map.matrix[x - i][y + j] = self


    def place_without_heuristic(self, x, y, map):
        for i in range(self.length):
            for j in range(self.breadth):
                map.matrix[x - i][y + j] = self

    def unplace_without_heuristic(self, x, y, map):
        for i in range(self.length):
            for j in range(self.breadth):
                map.matrix[x - i][y + j] = 0

    def is_constraints_valid(self,x, y, map):
        map_copy = map
        # First place the tent at x,y on map.
        # map_copy = copy.deepcopy(map)

        self.place_without_heuristic(x,y,map_copy)
        module = __import__("tents")

        # For all other existing tents, unplace them and see if you can place them there again, no constraints violated
        # print("okfr", map.btm_left_xy)
        for x1, y1, tent_type in map_copy.btm_left_xy:
            tent_type = getattr(module, tent_type)
            instance = tent_type()
            instance.unplace_without_heuristic(x1, y1, map_copy)
            # print(x1,y1)
            # print("map heurist")
            # for p in map_copy.printable():
            #     print(p)
            # if self.tent_type == "K9Tent" and x == 10 and y == 29 :
            #     print("reached")
            if not instance.place_possible(x1, y1, map_copy):
                instance.place_without_heuristic(x1, y1, map_copy)
                self.unplace_without_heuristic(x,y, map_copy)
                # instance.place_without_heuristic(x1, y1, map_copy)
                return False
            # self.unplace_without_heuristic(x,y, map_copy)
            instance.place_without_heuristic(x1, y1, map_copy)
        self.unplace_without_heuristic(x,y, map_copy)
        return True

    def place_possible(self, x, y, map):
        if self.tent_type in map.heuristic_matrix[x][y]:
            # if self.tent_type == "RestTent":

            # print("quack2")
            return False
        ## too big for the matrix
        if x - (self.length - 1) < 0 or y + self.breadth > map.breadth:
            # if self.tent_type == "RestTent":
            # print("quack3")
            return False
        ## too big for given space
        for i in range(self.length):
            for j in range(self.breadth):
                if map.matrix[x - i][y + j] != 0:  ## True equates to square already occupied
                    # print("no way")
                    # if self.tent_type == "RestTent":
                    # print("quack4")
                    return False

        x_topleft = max(0, x - self.length - self.spacing + 1)
        y_topleft = max(0, y - self.spacing)
        x_btmright = min(x + self.spacing +1, map.length)
        y_btmright = min(y + self.breadth + self.spacing , map.breadth)
        # print(self.tent_type)
        # spacing for walking / spaciousness

        for i in range(x_topleft, x_btmright):
            for j in range(y_topleft, y_btmright):
                # print(map.matrix[i][j], type(map.matrix[i][j]))
                # print(i,j)
                if type(map.matrix[i][j]) == int:
                    # if map.matrix[i][j] != 0:
                    #
                    #     # print("zzz")
                    #     return False
                    # else:
                    continue
                else:
                    if map.matrix[i][j].tent_type != "OutOfBoundsMarker":
                        # if map.matrix[i][j].tent_type == "DeconTent" and self.tent_type == "CleanTent":
                        #     continue
                        # if self.tent_type == "RestTent":
                        # for p in map.printable():
                        #     print(p)
                        # print(i,j)
                        # print(map.matrix[i][j].tent_type)
                        # print("quack5")
                        return False
        return True



class BigTent(GenericTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 3


class LogisticsTent(BigTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 4


class CommunityTent(BigTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 5


class UCCTent(BigTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 6


class SentryTent(BigTent):
    def __init__(self, length=4, breadth=4, entrance_xy: list = None):
        super().__init__(length, breadth)
        self.id = 7
        if entrance_xy is None:
            entrance_xy = [20, 0]
        self.entrance_xy = entrance_xy

    def place_possible(self, x, y, map):
        if not super().place_possible(x, y, map):
            return False
        if x not in range(self.entrance_xy[0] - self.length, self.entrance_xy[0] + self.length) or y not in range(
                self.entrance_xy[1] - self.breadth, self.entrance_xy[1] + self.breadth):
            return False
        return True


class BigClusterTent(BigTent):
    def getCluster(self, map):
        return map.messCluster

    def add_to_cluster(self, x, y, map):
        self.getCluster(map).append([x, y])

    def remove_from_cluster(self, x, y, map):
        # print(self.getCluster(map))
        self.getCluster(map).remove([x,y])

    def unplace2(self, x, y, map):
        super().unplace2(x,y,map)

        self.remove_from_cluster(x,y,map)
        # print("unplacecluster:",self.getCluster(map))

    def place2(self, x, y, map):
        super().place2(x,y,map)

        self.add_to_cluster(x,y,map)
        # print("placecluster:",self.getCluster(map))

    def place_possible(self, x, y, map):
        if not super().place_possible(x, y, map):
            #
            # if self.tent_type == "RestTent":
            # print("quack00")
            return False
        if len(self.getCluster(map)) == 0:

            return True
        else:

            for tent in self.getCluster(map):
                if tent[0] == x:
                    if tent[1] - self.breadth - self.spacing == y or tent[1] + self.breadth + self.spacing == y:
                        return True
                if tent[1] == y:
                    if tent[0] - self.length - self.spacing == x or tent[0] + self.length + self.spacing == x:
                        return True
            # print("quack1")
            # if self.tent_type == "RestTent":
            #     print(self.getCluster(map))
            # print("quack11")
            return False




class SmallClusterTent(BigClusterTent):
    def __init__(self, length=1, breadth=1):
        super().__init__(length, breadth)
        self.id = 8


class MessTent(BigClusterTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 9

    def getCluster(self, map):
        return map.messCluster


class MaintenanceTent(BigClusterTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 10

    def getCluster(self, map):
        return map.MainPOLCluster


class POLTent(BigClusterTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 11

    def getCluster(self, map):
        return map.MainPOLCluster


class MedicalTent(BigClusterTent):
    def __init__(self, length=2, breadth=4):
        super().__init__(length, breadth)
        self.id = 12

    def getCluster(self, map):
        return map.medicalCluster


class SpacedOutClusterTent(BigClusterTent):
    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 13
        self.clusterspacing = 4
        self.cluster_tent_names = ["DeconTent"]

    def getCluster(self, map):
        return map.cleanCluster

    def place_possible(self, x, y, map, ):
        if not super(SpacedOutClusterTent, self).place_possible(x, y, map):
            # print("1")
            return False
        ## Cleanliness 4-Metre Rule. Here we take 1 slot in the matrix = 1m^2 in real life
        # x_topleft = max(0, x - self.length - self.clusterspacing)
        # y_topleft = max(0, y - self.clusterspacing)
        # x_btmright = min(x + self.clusterspacing, map.length)
        # y_btmright = min(y + self.breadth + self.clusterspacing, map.breadth)

        x_topleft = max(0, x - self.length - self.clusterspacing + 1)
        y_topleft = max(0, y - self.clusterspacing)
        x_btmright = min(x + self.clusterspacing, map.length)
        y_btmright = min(y + self.breadth + self.clusterspacing + 1, map.breadth)
        for i in range(x_topleft, x_btmright):
            for j in range(y_topleft, y_btmright):
                # print(map.matrix[i][j], type(map.matrix[i][j]))
                if type(map.matrix[i][j]) == int:
                    # if map.matrix[i][j] != 0:
                    #     # print("2")
                    #     return False
                    # else:
                    continue
                else:

                    if map.matrix[i][j].tent_type not in self.cluster_tent_names and map.matrix[i][j].tent_type != 0:
                        # print("3")
                        return False
        return True


class CleanTent(SpacedOutClusterTent):
    def getCluster(self, map):
        return map.cleanCluster

    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 14
        self.clusterspacing = 4
        self.cluster_tent_names = ["CleanTent"]

    def place_possible(self, x, y, map):
        return super(CleanTent, self).place_possible(x, y, map)


class DeconTent(SpacedOutClusterTent):
    def getCluster(self, map):
        return map.cleanCluster

    def __init__(self, length=4, breadth=4):
        super().__init__(length, breadth)
        self.id = 99
        self.spacing = 4
        self.cluster_tent_names = ["CleanTent"]


class SpacedOutSmallClusterTent(SpacedOutClusterTent):
    def __init__(self, length=1, breadth=1):
        super().__init__(length, breadth)
        self.id = 15
        self.clusterspacing = 2
        self.cluster_tent_names = ["K9Tent"]

    def getCluster(self, map):
        return map.restCluster


class K9Tent(SpacedOutSmallClusterTent):
    def __init__(self, length=1, breadth=1):
        super().__init__(length, breadth)
        self.id = 16
        self.clusterspacing = 2
        self.cluster_tent_names = ["K9Tent"]

    def place_possible(self, x, y, map):
        is_beside_restCluster = False
        # print("debug")
        # for row in map.printable():
        #     print(row)
        if len(self.getCluster(map)) == 0:
            # print("debug2")
            if (x-self.length-self.clusterspacing >=0 and type(map.matrix[x-self.length-self.clusterspacing][y]) == tents.RestTent) or (x+self.length+self.clusterspacing < map.length and type(map.matrix[x+self.length+self.clusterspacing][y]) == tents.RestTent) or (y+self.breadth+self.clusterspacing < map.breadth and type(map.matrix[x][y+self.breadth+self.clusterspacing]) == tents.RestTent) or (y-self.breadth-self.clusterspacing >= 0 and type(map.matrix[x][y-self.breadth-self.clusterspacing]) == tents.RestTent):
                is_beside_restCluster = True
            if not is_beside_restCluster:
                return False
        return super(K9Tent, self).place_possible(x, y, map)

    def getCluster(self, map):
        return map.K9Cluster


class RestTent(SmallClusterTent):
    def __init__(self, length=1, breadth=1):
        super().__init__(length, breadth)
        self.id = 17

    def getCluster(self, map):
        return map.restCluster


class EnsuiteDuoTent(SmallClusterTent):
    def __init__(self, length=1, breadth=2):
        super().__init__(length, breadth)
        self.id = 18

    def getCluster(self, map):
        return map.ensuiteCluster
