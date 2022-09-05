import heapq as hq
import numpy as np
from passenger import Passenger
from city import City

class EventQueue:
    def __init__(self, T:float, lmd_m, id, city:City):
        # queue by time priority
        self.queue = []
        # dictionary to record passengers, key is passenger id, value is passenger 
        self.record = {}
        # dequeue list
        self.deq = []
        # dictionary to record passengers who is being served, key is passenger id, value is passenger 
        self.sketch_dict = {}

        # Initialize events info
        self.T, self.lmd_m, self.id, self.city, self.rng = T, lmd_m, id, city, np.random.default_rng(seed=2)
        self.clock = 0
        self.head_idx = 0
        
        max_zone_id = self.city.n**2-1
        for i in range(max_zone_id+1):
            for j in range(max_zone_id+1):
                t, idx = 0, 0
                lmd = lmd_m[i][j]
                ozone, dzone = self.city.zones[i], self.city.zones[j]
                while t < T:
                    dt = self.rng.exponential(scale=1/lmd)
                    t += dt
                    passenger = Passenger(t0=t, passenger_id=((i, j), idx, t), ozone=ozone, dzone=dzone)
                    self.queue.append((t, passenger))
                    self.record[passenger.id] = passenger
                    self.sketch_dict[passenger.id] = passenger
                    idx += 1
        self.queue.sort(key=lambda k : k[0])
        return 

    def move(self, dt):
        self.clock += dt
        return 

    # sketching_helper function
    def sketch_helper(self):
        px, py, popped_list = [], [], []
        for id in self.sketch_dict:
            passenger = self.sketch_dict[id]
            if (passenger.status == -1):
                popped_list.append(id)
            elif (self.clock > passenger.t_start):
                if (passenger.status != 2):
                # if (passenger.t_s == None or self.clock < passenger.t_s):
                    px.append(passenger.location()[0][0])
                    py.append(passenger.location()[0][1])
                else:
                    popped_list.append(id)
        for id in popped_list:
            self.sketch_dict.pop(id, None)
        return [px, py]

    def empty(self):
        return len(self.queue) == 0

    def head(self):
        p_id, p = self.queue[self.head_idx]
        return p_id, p

    # pop the event with the minimum time 
    # return the popped time and event
    def dequeue(self):
        p_id, p = self.head()
        self.head_idx += 1
        self.deq.append(p)
        return p_id, p
        




