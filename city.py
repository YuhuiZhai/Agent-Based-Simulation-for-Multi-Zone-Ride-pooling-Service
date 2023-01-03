import numpy as np
import matplotlib.pyplot as plt
class Zone:
    # prob is the tuple of probalbility traveling towards N, E, W, S
    def __init__(self, length=5, max_v=25.0, center=(0.5, 0.5), id=0):
        self.length, self.max_v, self.center, self.id = length, max_v, center, id
        self.rng = np.random.default_rng(seed=np.random.randint(100))

    # set the center of the zone
    def set_center(self, new_center:tuple):
        self.center = new_center
        return
    
    def xyrange(self):
        xlim = [self.center[0] - self.length/2, self.center[0] + self.length/2]
        ylim = [self.center[1] - self.length/2, self.center[1] + self.length/2] 
        return xlim, ylim

    # xlim and ylim defines the location restriction within this zone
    def generate_location(self, xlim=None, ylim=None):
        xlim0, ylim0 = self.xyrange()
        if xlim == None: 
            xlim = xlim0
        if ylim == None:
            ylim = ylim0
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

    def sketch(self, delta=0.985):
        x1, x2 = self.center[0] - self.length/2*delta, self.center[0] + self.length/2*delta
        y1, y2 = self.center[1] - self.length/2*delta, self.center[1] + self.length/2*delta  
        plt.fill_between([x1, x2], [y1, y1], [y2, y2], color="None", hatch="/", edgecolor="r")

    def print(self):
        print(f"length {self.length}, center {self.center}, prob {self.prob}")

class City:
    # n is the number of block per line
    # prob_matrix is the matrix containing delta_ij for each block having the form:
    # prob_matirx = [ (N_00,E_00,W_00,S_00), ... , (N_0n,E_0n,W_0n,S_0n)
    #                          ...                          ...     
    #                 (N_n0,E_n0,W_n0,S_n0), ... , (N_nn,E_nn,W_nn,S_nn)]
    def __init__(self, length:float, max_v=25.0, n=1, prob_matrix=None):
        self.length, self.max_v = length, max_v
        self.split(n, prob_matrix)
        # feasible zone is a dictionary storing Case 2 pair {key=(ozone_id, dzone_id) : value=[feasible zone id]}
        self.feasible_zone2 = {}
        # feasible zone is a dictionary storing Case 3 pair {key=(ozone_id, dzone_id) : value=[feasible zone id]}
        self.feasible_zone3 = {}
        self.init_omega()

    # intialize the omega set
    def init_omega(self):
        def dist(o, d):
            ox, oy = self.getZone(o).center
            dx, dy = self.getZone(d).center
            return abs(ox - dx) + abs(oy - dy)
        self.omega_sets = {}
        for i in range(self.n**2):
            for j in range(self.n**2):
                if j == i:
                    continue
                fz = self.feasibleZone_2(i, j)
                omega = set()
                for k in fz:
                    if dist(i, k) >= dist(i, j):
                        omega.add(k)
                self.omega_sets[(i, j)] = omega
        return 
    
    # return the direction of movement
    def direction_helper(self, xy1, xy2):
        temp = {(1, 0):"E", (0, 1):"N", (-1, 0):"W", (0, -1):"S",  
                (1, 1):"NE", (-1, 1):"NW", (-1, -1):"SW", (1, -1):"SE",
                (0, 0):"Same Point"}
        xdir, ydir = self.dir(xy1, xy2)
        dir = temp[(xdir, ydir)] 
        return dir

    # function for warming process
    def assignT(self, T):
        self.T = T
        return 

    def omega(self, i, j):
        return self.omega_sets[(i, j)]

    # function to split the city into n x n zones
    # If city was splitted before, this function will replace the city by a new one. 
    def split(self, n:int, prob_matrix=None):
        if prob_matrix == None:
            prob_matrix = [[(0.25, 0.25, 0.25, 0.25) for j in range(n**2)] for i in range(n**2)]
        self.n, self.l, self.prob_matrix = n, self.length/n, prob_matrix
        self.zone_matrix = []
        self.zones = {}
        for i in range(n):
            self.zone_matrix.append([])
            for j in range(n):
                center = ((j+0.5)*self.l, n*self.l-(i+0.5)*self.l)
                zone = Zone(length=self.l, max_v=self.max_v, center=center, id=int(i*n+j))
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
    
    # given two xy tuple, return the relative direction of xy2 to xy1 
    def dir(self, xy1:tuple, xy2:tuple):
        x1, y1 = xy1
        x2, y2 = xy2
        xdir, ydir = 0, 0
        if x2 > x1: xdir = 1
        elif x2 < x1: xdir = -1
        if y2 > y1: ydir = 1
        elif y2 < y1: ydir = -1
        return xdir, ydir        

    # Case 1 feasible region, return range of x, y
    def feasibleZone_1(self, c_oxy, c_dxy, c_zone_id:int):
        c_zone = self.zones[c_zone_id]
        xdir, ydir = self.dir(c_oxy, c_dxy)
        xlim1, ylim1 = [c_oxy[0], c_dxy[0]], [c_oxy[1], c_dxy[1]]
        xlim2, ylim2 = [c_dxy[0], c_zone.center[0] + xdir*self.l/2], [c_dxy[1], c_zone.center[1] + ydir*self.l/2]
        xlim1.sort(); xlim2.sort(); ylim1.sort(); ylim2.sort()
        return xlim1, ylim1, xlim2, ylim2

    # Case 2 feasible region, return list of feasible zones id
    def feasibleZone_2(self, c_ozone_id:int, c_dzone_id:int):
        c_ozone, c_dzone = self.zones[c_ozone_id], self.zones[c_dzone_id]
        xdir, ydir = self.dir(c_ozone.center, c_dzone.center)
        if xdir == 0 and ydir == 0:
            print("Error in Case 2")
            return 
        else:
            if (c_ozone_id, c_dzone_id) in self.feasible_zone2:
                return self.feasible_zone2[(c_ozone_id, c_dzone_id)]
            i1, j1 = c_ozone.ij
            i2, j2 = c_dzone.ij
            xlim1, ylim1 = [j1, j2], [i1, i2]
            xlim1.sort(); ylim1.sort()
            feasible_zone = []
            i3, j3 = int(-(ydir - 1)*1/2*(self.n-1)), int((1 + xdir)*1/2*(self.n-1))
            for i in range(ylim1[0], ylim1[1]+1):
                for j in range(xlim1[0], xlim1[1]+1):
                    zone_id = self.zone_matrix[i][j].id
                    if zone_id == c_ozone.id or zone_id == c_dzone.id:
                        continue
                    feasible_zone.append(zone_id)
            # od are not aligned in the same diretcion
            if xdir != 0 and ydir != 0:
                xlim2, ylim2 = [j2, j3], [i2, i3]
                xlim2.sort(); ylim2.sort()
                for i in range(ylim2[0], ylim2[1]+1):
                    for j in range(xlim2[0], xlim2[1]+1):
                        feasible_zone.append(self.zone_matrix[i][j].id)
            # od are aligned in the same diretcion
            else:
                if xdir == 0:
                    ylim2 = [i2, i3]; ylim2.sort()
                    for i in range(ylim2[0], ylim2[1]+1):
                        for j in range(0, self.n):
                            feasible_zone.append(self.zone_matrix[i][j].id)
                else:
                    xlim2 = [j2, j3]; xlim2.sort()
                    for i in range(0, self.n):
                        for j in range(xlim2[0], xlim2[1]+1):
                            feasible_zone.append(self.zone_matrix[i][j].id)
            self.feasible_zone2[(c_ozone_id, c_dzone_id)] = feasible_zone
        return feasible_zone

    # Case 3 feasible region, return list of feasible zones 
    def feasibleZone_3(self, c_oxy, c_dxy, c_zone_id:int):
        xdir, ydir = self.dir(c_oxy, c_dxy)
        if xdir == 0 and ydir == 0:
            print("Error in Case 3")
            return 
        if (c_zone_id, (xdir, ydir)) in self.feasible_zone3:
            return self.feasible_zone3[(c_zone_id, (xdir, ydir))]
        c_zone = self.zones[c_zone_id]
        i1, j1 = c_zone.ij
        feasible_zone = []
        i2, j2 = int(-(ydir - 1)*1/2*(self.n-1)), int((1 + xdir)*1/2*(self.n-1))
        if xdir != 0 and ydir != 0:
            ylim1, xlim1 = [i1, i2], [j1, j2] 
            ylim1.sort(); xlim1.sort()
            for i in range(ylim1[0], ylim1[1]+1):
                for j in range(xlim1[0], xlim1[1]+1):
                    zone_id = self.zone_matrix[i][j].id
                    if zone_id == c_zone_id:
                        continue
                    feasible_zone.append(zone_id)
        elif xdir == 0:
            ylim1 = [i1, i2]
            ylim1.sort()
            for i in range(ylim1[0], ylim1[1]+1):
                zone_id = self.zone_matrix[i][j1].id
                if zone_id == c_zone_id:
                    continue
                feasible_zone.append(zone_id)
        else:
            xlim1 = [j1, j2]
            xlim1.sort()
            for j in range(xlim1[0], xlim1[1]+1):
                zone_id = self.zone_matrix[i1][j].id
                if zone_id == c_zone_id:
                    continue
                feasible_zone.append(zone_id)
        self.feasible_zone3[(c_zone_id, (xdir, ydir))] = feasible_zone
        return feasible_zone

    # Case 4 feasible region, input is passenger's origin (x, y), origin zone id, destination zone id 
    def feasibleZone_4(self, c_oxy:tuple, c_ozone_id:int, c_dzone_id:int):
        # get the zone object
        c_ozone, c_dzone = self.zones[c_ozone_id], self.zones[c_dzone_id]
        # get the relative direction of destination to origin
        xdir, ydir = self.dir(c_ozone.center, c_dzone.center)
        diag = False
        # diagonal case
        if xdir != 0 and ydir != 0:
            diag = True
            xlim, ylim = [c_oxy[0], c_ozone.center[0]+xdir*self.l/2], [c_oxy[1], c_ozone.center[1]+ydir*self.l/2]
        elif xdir == 0:
            xlim, ylim = [c_ozone.center[0]-self.l/2, c_ozone.center[0]+self.l/2], [c_oxy[1], c_ozone.center[1] + ydir*self.l/2]    
        else:
            xlim, ylim = [c_oxy[0], c_ozone.center[0]+xdir*self.l/2], [c_ozone.center[1]-self.l/2, c_ozone.center[1]+self.l/2]        
        xlim.sort(); ylim.sort()
        return xlim, ylim, diag

    def getZone(self, zone_id:int):
        return self.zones[zone_id]

    def sketch(self):
        for i in range(self.n+1):
            plt.plot([0, self.length], [i*self.l, i*self.l], 'g')
        for i in range(self.n+1):
            plt.plot([i*self.l, i*self.l], [0, self.length], 'g')
        return 

    # sketch wanted zones
    def sketchZone(self, zone_ids:list):
        for zone_id in zone_ids:
            zone = self.zones[zone_id]
            zone.sketch()
        return 