import heapq as hq
import numpy as np
from passenger import Passenger
from city import City

class EventQueue:
    def __init__(self, city:City, T:float, lmd:float, id, rng=None):
        # queue by time priority
        self.queue = []
        # dictionary to record passengers, key is passenger id, value is passenger 
        self.record = {}
        # dictionary to record passengers who is being served, key is passenger id, value is passenger 
        self.sketch_dict = {}
        self.city, self.T, self.lmd, self.id, self.rng = city, T, lmd, id, np.random.default_rng(seed=2)
        self.size = 0
        self.clock = 0
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

    # add an event to the queue
    # type of event is class Node
    def head(self):
        p_id, p = self.queue[0]
        return p_id, p

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
        return p_id, p

    # return the passenger assigned time 
    def info(self):
        totalt1, totalt2, totalt3 = [], [], []
        at1, at2, at3 = [], [], []
        for id in self.record:
            pax = self.record[id]
            if pax.t_end == None:
                continue
            totalt3.append(pax.t_end - pax.t_start)
            at3.append(pax.t_s - pax.t_start)
            if not pax.shared:
                totalt1.append(pax.t_end - pax.t_start)
                at1.append(pax.t_s - pax.t_start)
            else:
                totalt2.append(pax.t_end - pax.t_start)
                at2.append(pax.t_s - pax.t_start)
        
        total_t1 = np.average(np.array(totalt1)) if len(totalt1) != 0 else 0
        total_t2 = np.average(np.array(totalt2)) if len(totalt2) != 0 else 0
        total_t3 = np.average(np.array(totalt3)) if len(totalt3) != 0 else 0
        a_t1 = np.average(np.array(at1)) if len(at1) != 0 else 0
        a_t2 = np.average(np.array(at2)) if len(at2) != 0 else 0
        a_t3 = np.average(np.array(at3)) if len(at3) != 0 else 0
        return (totalt1, totalt2, totalt3), (total_t1, total_t2, total_t3), (at1, at2, at3), (a_t1, a_t2, a_t3)