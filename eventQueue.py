import heapq as hq
import random
from unit import Unit
from passenger import Passenger
from city import City

class Event:
    def __init__(self, time, event_type, vehicle:Unit, passenger:Passenger):
        self.time = time
        self.type = event_type
        self.vehicle = vehicle
        self.passenger = passenger

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
        temp_passenger_id = 0
        while t < T:
            dt = random.expovariate(lmd)
            t += dt
            temp_passenger = Passenger(t, (self.id, temp_passenger_id), city)
            temp_passenger_id += 1
            event = Event(temp_passenger.t_start, 'appear', None, temp_passenger)
            self.insert(event)
    
    def move(self, dt):
        self.clock += dt

    # sketching_helper function
    def sketch_helper(self):
        px, py, popped_list = [], [], []
        for id in self.sketch_dict:
            passenger = self.sketch_dict[id]
            if (passenger.status == "unserved"):
                popped_list.append(id)
            elif (self.clock > passenger.t_start):
                if (passenger.t_s == None or self.clock < passenger.t_s):
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
        head_time, head = self.queue[0]
        return head_time, head

    def insert(self, event:Event):
        self.size += 1
        hq.heappush(self.queue, (event.time, event))
        self.record[event.passenger.id] = event.passenger
        self.sketch_dict[event.passenger.id] = event.passenger

    # pop the event with the minimum time 
    # return the popped time and event
    def dequeue(self):
        self.size -= 1
        time, event = hq.heappop(self.queue)
        return time, event

    # return the passenger assigned time 
    def info(self):
        ta = []
        for id in self.record:
            pax = self.record[id]
            if (pax.t_s == None):
                continue
            ta.append(pax.t_s - pax.t_start)
        return sum(ta)/len(ta) 