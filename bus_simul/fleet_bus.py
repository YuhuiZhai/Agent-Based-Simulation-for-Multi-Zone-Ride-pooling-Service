from fleet import Fleet
from city import City
from city import CityNode
from passenger import Passenger
import heapq as hq
class Stop(CityNode):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.queue = []

    def inqueue(self, passenger:Passenger):
        hq.heappush(self.queue, (passenger., ))

class Busfleet(Fleet):
    def __init__(self, n:int, city:City, id):
        super().__init__(n, city, id)   
        self.init_group(
            status_name={0:"stopping", 1:"moving"},
            status_num={0:0, 1:n}
        )
        for i in range(n):
            veh = Vehicle((self.id, i), city)
            self.vehicles[(self.id, i)] = veh
            self.vehs_group[1].add(veh)
    
    def addRoute(route:list):
