from city import City
from unit import Unit
import utils
import math
class Bus(Unit):
    def __init__(self, bus_id, city:City, terminal=(0, 0), route=[], t0=0, tau=120/3600):
        super().__init__(bus_id, city, init_status=1)
        self.status_table = {0:"stopping", 1:"driving"}
        self.clock = 0
        (self.x, self.y), self.route, self.t_start, self.tau = terminal, route, t0, tau
        self.speed = city.max_v
        self.next_sta = 0
        self.waiting_time = tau
        self.capacity = math.inf
        self.count = 0

    def move(self, dt):
        self.count += 1
        # if self.count % 100 == 0:
            # print((self.x, self.y), (self.city.stoplist[self.next_sta].x, self.city.stoplist[self.next_sta].y))
        status_request = (self.id, -1, -1)
        self.clock += dt
        if self.clock < self.t_start or len(self.route) == 0:
            return status_request
        reached = self.move_Euclidean(dt, self.route[self.next_sta])
        if reached:
            status_request = self.changeStatusTo(0)
            if self.waiting_time <= 0:
                self.waiting_time = self.tau
                self.next_sta = (self.next_sta + 1)%len(self.route)
                status_request = self.changeStatusTo(1)
            else: self.waiting_time -= dt 
            return status_request
   
    def location(self):
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":  
            return (self.x, self.y)

        if self.city.type_name == "real-world":
            (x, y) = utils.location_helper(self.link, self.len)
            return (x, y)