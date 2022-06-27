import heapq as hq
import random
from passenger import Passenger
from city import City

class EventQueue:
    def __init__(self, city:City, T:float, lmd:float, id):
        # queue by time priority
        self.queue = []
        # dictionary to record passengers, key is passenger id, value is passenger 
        self.record = {}
        # dictionary to record passengers who is being served, key is passenger id, value is passenger 
        self.sketch_dict = {}
        self.city, self.T, self.lmd, self.id = city, T, lmd, id
        self.size = 0
        self.clock = 0
        t = 0
        passenger_id = 0
        while t < T:
            dt = random.expovariate(lmd)
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
        s1, s2, s3 = [], [], []
        for id in self.record:
            pax = self.record[id]
            if pax.t_end == None:
                continue
            s3.append(pax.t_end - pax.t_start)
            if not pax.shared:
                s1.append(pax.t_end - pax.t_start)
            else:
                s2.append(pax.t_end - pax.t_start)
        total_t1 = sum(s1)/len(s1) if len(s1) != 0 else 0
        total_t2 = sum(s2)/len(s2) if len(s2) != 0 else 0
        total_t3 = sum(s3)/len(s3) if len(s3) != 0 else 0
        
        mid1 = s1[int(len(s1)/2)] if len(s1) != 0 else 0
        mid2 = s2[int(len(s2)/2)] if len(s2) != 0 else 0
        mid3 = s3[int(len(s3)/2)] if len(s3) != 0 else 0
        return (s1, s2, s3), (total_t1, total_t2, total_t3), (mid1, mid2, mid3)