import matplotlib.pyplot as plt
import heapq as hq
import utils 
from tqdm import tqdm

def assign_type():
        table = {"1":"Euclidean", "2":"Manhattan", "3":"real-world", 
                "Euclidean":"Euclidean", "Manhattan":"Manhattan", "real-world":"real-world"}
        print("Please enter the type of city? \n [1: Euclidean, 2:Mahattan, 3:real-world]")
        answer = input()
        if answer in table.keys():
            return table[answer]
        else:
            print("Wrong input, please try again")
            return 

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
    def __init__(self, type_name=""):
        # 3 types: Eucledean, Manhatten, real-world
        self.type_name = type_name 
        self.num_node = 0
        self.num_link = 0
        # dictionary of nodes
        # key is id, value is citynode
        self.nodes = {}
        # dictionary of links
        # key is id, value is citylink
        self.links = {}
        # key is (node1_id, node2_id), value is citylink_id
        self.map = {}
        # dictionary of shortest path
        # key is O,D, value is distance and path []
        # dj_path[o, d] = dist, [o, node1, node2, ..., d]
        self.dj_path = {}
        # neighbour
        # key is node, value is list of neighbour node
        self.neigh = {}
        if (self.type_name == ""):
            type = assign_type()
            while (type == None):
                type = assign_type()
            self.type_name = type

    def add_node(self, new_node:CityNode):
        # add new citynode by its id 
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
    
    def sketch(self):
        if (self.type_name == "real-world"):
            for idx, key in enumerate(self.links):
                link = self.links[key]
                plt.plot([link.ox, link.dx], [link.oy, link.dy], color = 'k') 
        return 

    def sketchpath(self):
        dist, path = self.dj_path[0, 100]
        for i in range(1, len(path)):
            link = self.links[self.map[path[i-1], path[i]]]
            plt.plot([link.ox, link.dx], [link.oy, link.dy], color = 'r') 

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