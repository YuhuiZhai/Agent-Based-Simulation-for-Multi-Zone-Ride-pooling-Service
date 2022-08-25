import numpy as np
class Zone:
    # prob is the tuple of probalbility traveling towards N, E, W, S
    def __init__(self, length=3.6, max_v=18.0, center=(0.5, 0.5), id=0, prob=(0.25, 0.25, 0.25, 0.25)):
        self.length, self.max_v, self.center, self.id = length, max_v, center, id
        self.rng = np.random.default_rng(seed=3)
        self.prob = prob

    # set the center of the zone
    def set_center(self, new_center:tuple):
        self.center = new_center
        return
    
    def generate_location(self):
        x = self.origin[0] + self.length*self.rng.random()
        y = self.origin[1] + self.length*self.rng.random()
        return x, y 

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
            print("Error in no prob_matrix")
            return     
        self.n, self.l, self.prob_matrix = n, self.length/n, prob_matrix
        self.zone_matrix = []
        for i in range(n):
            self.zone_matrix.append([])
            for j in range(n):
                center = ((j+0.5)*self.l, n*self.l-(i+0.5)*self.l)
                zone = Zone(length=self.l, max_v=self.max_v, center=center, id=int(i*n+j), prob=prob_matrix[i][j])
                self.zone_matrix[i].append(zone)
