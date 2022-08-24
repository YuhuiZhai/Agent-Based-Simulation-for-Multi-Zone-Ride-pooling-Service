import heapq as hq
import numpy as np
from passenger import Passenger
from city import City

class EventQueue:
    def __init__(self, city:City, T:float, lmd:float, id):
        # queue by time priority
        self.queue = []
        # dictionary to record passengers, key is passenger id, value is passenger 
        self.record = {}
        # dequeue list
        self.deq = []
        # dictionary to record passengers who is being served, key is passenger id, value is passenger 
        self.sketch_dict = {}

        # Initialize events info
        self.city, self.T, self.lmd, self.id, self.rng = city, T, lmd, id, np.random.default_rng(seed=2)
        self.size = 0
        self.clock = 0
        
        # Initialize passenger info
        t = 0
        passenger_id = 0
        while t < T:
            # dt = random.expovariate(lmd)
            dt = self.rng.exponential(scale=1/lmd)
            t += dt
            passenger = Passenger(t, (self.id, passenger_id), city)
            passenger_id += 1
            self.insert(passenger)

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
        p_id, p = self.queue[0]
        return p_id, p

    # insert a passenger to the list, the smaller the id, the greater the priority
    def insert(self, passenger:Passenger):
        self.size += 1
        hq.heappush(self.queue, (passenger.id, passenger))
        self.record[passenger.id] = passenger
        self.sketch_dict[passenger.id] = passenger

    # pop the event with the minimum time 
    # return the popped time and event
    def dequeue(self):
        self.size -= 1
        p_id, p = hq.heappop(self.queue)
        self.deq.append(p)
        return p_id, p