import matplotlib.pyplot as plt
import heapq as hq
import utils 
from tqdm import tqdm
import numpy as np
import xlrd
from collections import deque
import math

def assign_type():
        table = {"1":"Euclidean", "2":"Manhattan", "3":"real-world", 
                "Euclidean":"Euclidean", "Manhattan":"Manhattan", "real-world":"real-world"}
        print("Please enter the type of city? \n [1: Euclidean, 2:Manhattan, 3:real-world]")
        answer = input()
        if answer in table.keys():
            return table[answer]
        else:
            print("Wrong input, please try again")
            return 
class Stop:
    def __init__(self, id, location:tuple):
        self.id, self.location = id, location
        self.queue = deque()
    
    def inqueue(self, unit):
        self.queue.append(unit)
    
    def dequeue(self):
        return self.queue.pop()
    
    # function to release 
    def release(self, num):
        count, release_list = 0, set()
        while self.queue and count < num:
            release_list.add(self.dequeue())
            num += 1
        return release_list

class CityNode:
    def __init__(self, id, x, y):
        # x, y is the longnitude and latitude
        self.id = int(id)
        self.x = x
        self.y = y
        # neighbour citynode
        self.neighbour = {}
        # citylink between this node and neighbour citynode
        self.adjacent = {}
        # distance of citylink between this node and neighbour citynode
        self.dist2neighbour = {}

    def add_link(self, next_node, link):
        # next_node is added citynode
        # link is added citylink
        self.neighbour[next_node.id] = next_node
        self.adjacent[link.id] = link
        self.dist2neighbour[next_node.id] = link.length


class CityLink:
    def __init__(self, id, origin:CityNode, destination:CityNode):
        self.id = int(id)
        # origin and destination citynode
        self.origin = origin
        self.destination = destination
        self.ox = self.origin.x
        self.oy = self.origin.y
        self.dx = self.destination.x
        self.dy = self.destination.y
        self.length = utils.onplotdist(self.origin, self.destination)

    
class City:
    def __init__(self, type_name="", length=3.6, max_v=18.0, origin=(0, 0), node_file="", link_file=""):
        # 3 types: Eucledean, Manhatten, real-world
        self.type_name, self.length, self.max_v, self.origin = type_name, length, max_v, origin
        self.rng = np.random.default_rng(seed=3)
        self.node_file, self.link_file = node_file, link_file
        self.stoplist = []
        self.route = []
        if (self.type_name == ""):
            type = assign_type()
            while (type == None):
                type = assign_type()
            self.type_name = type
        if (self.type_name == "real-world"):
            self.num_node, self.num_link = 0, 0
            # key is id, value is citynode
            self.nodes = {}
            # key is id, value is citylink
            self.links = {}
            # key is (node1_id, node2_id), value is citylink_id
            self.map = {}
            # key is node, value is list of neighbour node
            self.neigh = {}
            self.init()

    def set_origin(self, new_origin:tuple):
        self.origin = new_origin
        return 

    def add_stops(self, stop_loc:list):
        for i, stopxy in enumerate(stop_loc):
            self.stoplist.append(Stop(i, stopxy))

    def nearest_stop(self, loc:tuple):
        min_dist = math.inf
        opt_stop = None
        x, y = loc
        for stop in self.stoplist:
            stopx, stopy = stop.location
            dist = ((stopx - x)**2 + (stopy - y)**2)**(0.5)
            if dist < min_dist:
                min_dist = dist
                opt_stop = stop
        return min_dist, opt_stop

    def add_route(self, route:list):
        self.route = route

    def add_node(self, new_node:CityNode):
        self.num_node += 1
        self.nodes[new_node.id] = new_node

    def add_link(self, new_link:CityLink):
        # if either nodes is not existed then do not add this new_link
        if (new_link.origin.id not in self.nodes or new_link.destination.id not in self.nodes):
            return 
        # add link to link dict with link id
        self.links[new_link.id] = new_link
        # add the link to the map dict with OD ids 
        self.map[new_link.origin.id, new_link.destination.id] = new_link.id
        # update the neighbour of both OD
        if new_link.origin.id not in self.neigh:
            self.neigh[new_link.origin.id] = [new_link.destination.id]
        else: self.neigh[new_link.origin.id].append(new_link.destination.id)    
        self.num_link += 1
    
    def generate_location(self):
        if self.type_name == "Euclidean" or self.type_name == "Manhattan":  
            x = self.origin[0] + self.length*self.rng.random()
            y = self.origin[1] + self.length*self.rng.random()
            return x, y 

        if self.type_name == "real-world":
            n_max = self.num_link
            idx = self.rng.integers(low=0, high=n_max-1)
            l = self.rng.random() * self.links[idx].length / 2
            return self.links[idx], l

    def init(self):
        if self.type_name != "real-world":
            return
        if self.node_file == "" or self.link_file == "":
            print("Incorrect file input")
            return 
        workbook1 = xlrd.open_workbook(self.node_file)
        worksheet1 = workbook1.sheet_by_index(0)
        num_nodes = worksheet1.nrows
        for row in range(1, num_nodes):
            temp_id = int(worksheet1.cell_value(row, 0))
            temp_x = worksheet1.cell_value(row, 1)
            temp_y = worksheet1.cell_value(row, 2)
            self.add_node(CityNode(temp_id, temp_x, temp_y))

        workbook2 = xlrd.open_workbook(self.link_file)
        worksheet2 = workbook2.sheet_by_index(0)
        num_links = worksheet2.nrows
        for row in range(1, num_links):
            temp_id = int(worksheet2.cell_value(row, 0))
            temp_origin = self.nodes[int(worksheet2.cell_value(row, 1))]
            temp_destination =\
            self.nodes[int(worksheet2.cell_value(row, 2))]
            self.add_link(CityLink(temp_id, temp_origin, temp_destination))
        print("read file completed")
        return

    def sketch(self):
        if self.type_name != "real-world":
            stopx, stopy = [], []
            for stop in self.stoplist:
                stopx.append(stop.location[0])
                stopy.append(stop.location[1])
            plt.plot(stopx, stopy, 'mD')
            for i in range(len(self.route)):
                prev_id, curr_id = self.route[i-1], self.route[i]
                prev_stop, curr_stop = self.stoplist[prev_id], self.stoplist[curr_id]
                plt.plot([prev_stop.location[0], curr_stop.location[0]], [prev_stop.location[1], curr_stop.location[1]], 'c-')
            
        else:
            for idx, key in enumerate(self.links):
                link = self.links[key]
                plt.plot([link.ox, link.dx], [link.oy, link.dy], color = 'k') 
        return 

    def dijkstra(self, start_id:int, end_id:int):
        if (start_id == end_id):
            return 0, [start_id]
        # heapqueue 
        queue = []
        # dict to check visited node
        vis = set()
        # dict of weight (distance)
        dist = {}
        # dict of previous smallest weight node path
        path = {}
        for i in range(self.num_node):
            path[i] = -1
        # push with a tuple (weight, node_id, previous node_id)
        hq.heappush(queue, (0, start_id, -1))
        while len(queue) != 0:
            weight, curr, prev = hq.heappop(queue)
            if curr not in vis:
                vis.add(curr)
            else:
                continue
            dist[curr] = weight
            path[curr] = prev
            neigh = self.neigh[curr]
            node_1 = self.nodes[curr]
            for n in neigh:
                if n not in self.neigh:
                    continue
                node_2 = self.nodes[n]
                hq.heappush(queue, (weight + utils.onplotdist(node_1, node_2), n, curr))
        if path[end_id] == -1:
            return -1, [] 
        dj_path = []
        curr_id = end_id
        while curr_id != -1:
            dj_path.append(curr_id)
            curr_id = path[curr_id]
        dj_path.reverse()
        return dist[end_id], dj_path