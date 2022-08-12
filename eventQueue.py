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
        # dequeue list
        self.deq = []
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
        self.deq.append(p)
        return p_id, p

    def batch_info(self, combined=True, steady=False):
        # matching time, assigned time, total traveling time 
        tm, ta, ts, t = [], [], [], []
        
        # for pax in self.deq:
        #     if pax.t_end == None:
        #         continue
        #     tm.append(pax.t_a - pax.t_start)
        #     ta.append(pax.t_s - pax.t_a)
        #     ts.append(pax.t_end - pax.t_s)
        #     t.append(pax.t_end - pax.t_start)
 
        for id in self.record:
            pax = self.record[id]
            if steady and pax.t_start <= self.clock*1/10:
                continue
            if combined:
                if pax.t_a == None:
                    tm.append(self.clock - pax.t_start)
                else:
                    tm.append(pax.t_a - pax.t_start)
            else:
                if pax.t_a == None:
                    continue
                else:
                    tm.append(pax.t_a - pax.t_start)
            if pax.t_s == None:
                continue 
            ta.append(pax.t_s- pax.t_a)
            if pax.t_end == None:
                continue
            ts.append(pax.t_end - pax.t_s)
            t.append(pax.t_end - pax.t_start)
        avgtm = sum(tm) / len(tm) if len(tm) != 0 else -1
        avgta = sum(ta) / len(ta) if len(ta) != 0 else -1
        avgts = sum(ts) / len(ts) if len(ts) != 0 else -1
        avgt = sum(t) / len(t) if len(t) != 0 else -1
        return (tm, ta, ts, t), (avgtm, avgta, avgts, avgt)

    def sharing_info(self):
        # 1 : served by idle taxi, 2 : served by rider sharing, 3 : combined
        t1, t2, t3 = [], [], []
        ta1, ta2, ta3 = [], [], []
        for id in self.record:
            pax = self.record[id]
            if pax.t_end == None:
                continue
            t3.append(pax.t_end - pax.t_start)
            ta3.append(pax.t_s - pax.t_start)
            if not pax.shared:
                t1.append(pax.t_end - pax.t_start)
                ta1.append(pax.t_s - pax.t_start)
            else:
                t2.append(pax.t_end - pax.t_start)
                ta2.append(pax.t_s - pax.t_start)
        avgt1 = np.average(np.array(t1)) if len(t1) != 0 else 0
        avgt2 = np.average(np.array(t2)) if len(t2) != 0 else 0
        avgt3 = np.average(np.array(t3)) if len(t3) != 0 else 0
        avgta1 = np.average(np.array(ta1)) if len(ta1) != 0 else 0
        avgta2 = np.average(np.array(ta2)) if len(ta2) != 0 else 0
        avgta3 = np.average(np.array(ta3)) if len(ta3) != 0 else 0
        return (t1, t2, t3), (avgt1, avgt2, avgt3), (ta1, ta2, ta3), (avgta1, avgta2, avgta3)