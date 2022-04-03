from tkinter.messagebox import NO
import matplotlib.pyplot as plt
import heapq as hq
import utils 
from tqdm import tqdm

class City:
    def __init__(self):
        self.num_node = 0
        self.num_link = 0
        # dictionary of nodes
        # key is id, value is citynode
        self.nodes = {}
        # dictionary of links
        # key is id, value is citylink
        self.links = {}
        # dictionary of map
        self.map = {}
        # dictionary of shortest path
        # key is O,D, value is distance and path []
        # dj_path[o, d] = dist, [o, node1, node2, ..., d]
        self.dj_path = {}
        # neighbour
        # key is node, value is list of neighbour node
        self.neigh = {}

    def add_node(self, new_node):
        
        # add new citynode by its id 
        self.num_node += 1
        self.nodes[new_node.id] = new_node

    def add_link(self, new_link):
        # if either nodes is not existed then do not add this new_link
        if (new_link.origin.id not in self.nodes or new_link.destination.id not in self.nodes):
            # print("link ", new_link.id, "cannot be constructed")
            return 
        # add link to link dict with link id
        self.links[new_link.id] = new_link

        # access the original citynode in citynode dict and add link to the destination citynode
        # redundant
        # self.nodes[new_link.origin.id].add_link(new_link.destination, new_link)

        # add the link to the map dict with OD ids 
        self.map[new_link.origin.id, new_link.destination.id] = new_link.id

        # update the neighbour of both OD
        if new_link.origin.id not in self.neigh:
            self.neigh[new_link.origin.id] = [new_link.destination.id]
        else: self.neigh[new_link.origin.id].append(new_link.destination.id)
        
        self.num_link += 1
        
        # print("link created successfully")

    def print(self):
        for idx, key in enumerate(self.nodes):
            node = self.nodes[key]
            plt.plot(node.x, node.y, color = 'b', marker = 'o')

        for idx, key in enumerate(self.links):
            link = self.links[key]
            plt.plot([link.ox, link.dx], [link.oy, link.dy], color = 'red') 
        plt.show()
        return self.nodes, self.links


    def dijkstra_helper(self, source):
        # heapqueue 
        queue = []
        # dict to check visited node
        vis = set()
        # dict of weight (distance)
        dist = {}
        # dict of previous smallest weight node path
        path = {}
        # push with a tuple (weight, node_id, previous node_id)
        hq.heappush(queue, (0, source, None))
        
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
                hq.heappush(queue, (weight + utils.distance(node_1, node_2), n, curr))

        return dist, path 

    # derive and return the dj_path
    def dijkstra(self):
        # first loop is to apply dijkstra to node i 
        connected = set()
        for i in tqdm(self.nodes.keys(), desc="Dijkstra"):
            if i not in self.neigh:
                continue
            connected.add(i)
            dist, path = self.dijkstra_helper(i)
            # second loop is to figure out optimal distance and path 
            for j in self.nodes.keys(): 
                if j not in path:
                    continue
                # opt_path is the optimal path 
                opt_path = [j]
                curr = path[j]
                while curr is not None:
                    opt_path.append(curr)
                    curr = path[curr]
                opt_path.reverse()

                self.dj_path[i, j] = dist[j], opt_path 
        return self.dj_path, connected
    