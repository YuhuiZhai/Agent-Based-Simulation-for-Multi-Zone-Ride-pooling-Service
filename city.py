import numpy as np
import matplotlib.pyplot as plt
class Zone:
    # prob is the tuple of probalbility traveling towards N, E, W, S
    def __init__(self, length=3.6, max_v=18.0, center=(0.5, 0.5), id=0, prob=(0.25, 0.25, 0.25, 0.25)):
        self.length, self.max_v, self.center, self.id = length, max_v, center, id
        self.rng = np.random.default_rng(seed=20)
        self.prob = prob

    # set the center of the zone
    def set_center(self, new_center:tuple):
        self.center = new_center
        return
    
    # xlim and ylim defines the location restriction within this zone
    def generate_location(self, xlim=None, ylim=None):
        if xlim == None: 
            xlim = [self.center[0] - self.length/2, self.center[0] + self.length/2]
        if ylim == None:
            ylim = [self.center[1] - self.length/2, self.center[1] + self.length/2] 
        xlim.sort()
        ylim.sort()
        lengthx, lengthy = abs(xlim[1] - xlim[0]), abs(ylim[1] - ylim[0])
        centerx, centery = (xlim[0] + xlim[1])/2, (ylim[0] + ylim[1])/2  
        x = centerx - lengthx/2 + lengthx*self.rng.random() 
        y = centery - lengthy/2 + lengthy*self.rng.random() 
        return x, y 

    def recordij(self, ij:tuple):
        self.ij = ij
        return 

    def print(self):
        print(f"length {self.length}, center {self.center}, prob {self.prob}")

class City:
    # n is the number of block per line
    # prob_matrix is the matrix containing delta_ij for each block having the form:
    # prob_matirx = [ (N_00,E_00,W_00,S_00), ... , (N_0n,E_0n,W_0n,S_0n)
    #                          ...                          ...     
    #                 (N_n0,E_n0,W_n0,S_n0), ... , (N_nn,E_nn,W_nn,S_nn)]
    def __init__(self, length:float, max_v=18.0, n=1, prob_matrix=None):
        self.length, self.max_v = length, max_v
        self.split(n, prob_matrix)

    # function to split the city into n x n zones
    # If city was splitted before, this function will replace the city by a new one. 
    def split(self, n:int, prob_matrix):
        if prob_matrix == None:
            prob_matrix = [[(0.25, 0.25, 0.25, 0.25) for j in range(n)] for i in range(n)]
        self.n, self.l, self.prob_matrix = n, self.length/n, prob_matrix
        self.zone_matrix = []
        self.zones = {}
        for i in range(n):
            self.zone_matrix.append([])
            for j in range(n):
                center = ((j+0.5)*self.l, n*self.l-(i+0.5)*self.l)
                zone = Zone(length=self.l, max_v=self.max_v, center=center, id=int(i*n+j), prob=prob_matrix[i][j])
                zone.recordij((i, j))
                self.zones[zone.id] = zone
                self.zone_matrix[i].append(zone)
    
    # function to return the adjacent neigbour zone given a direction 
    def neighborZone(self, zone:Zone, dir:int):
        dir_map = {0:(-1, 0), 1:(0, 1), 2:(0, -1), 3:(1, 0)}
        deltai, deltaj = dir_map[dir]
        i, j = zone.ij
        new_i, new_j = i+deltai, j+deltaj
        if new_i < 0 or new_i >= self.n or new_j < 0 or new_j >= self.n: 
            print("Error in neighborZone")
            return
        neighbour_zone = self.zone_matrix[new_i][new_j]
        return neighbour_zone
    
    def getZone(self, zone_id:int):
        return self.zones[zone_id]

    def sketch(self):
        for i in range(self.n+1):
            plt.plot([0, self.length], [i*self.l, i*self.l], 'g')
        for i in range(self.n+1):
            plt.plot([i*self.l, i*self.l], [0, self.length], 'g')
        return 