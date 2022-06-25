from urllib import request
from passenger import Passenger
from city import City
from unit import Unit
import utils

class Taxi(Unit):
    def __init__(self, vehicle_id:tuple, city:City, init_status):
        super().__init__(vehicle_id, city, init_status)
        self.status_table = {0:"assigned", 1:"in_service", 2:"idle", 3:"interchanged"}
        # around 30 mph
        self.speed = city.max_v
        self.load = 0
        # self.status = 2
        self.passenger = []
        # ordered list of passed nodes [..., cityNode1, cityNode2, cityNode3, ...]
        self.path1, self.path2 = [], []  
        # determine whether the pre-assigned route is finished "real-world"
        self.start1 = True
        # distance of assigned, distance of service
        self.dist_a, self.dist_s = 0, 0        
        # assigned time and inservice time
        self.ta, self.ts = 0, 0 
        # frequency of being called
        self.freq = 0
    
    def changeCity(self, city:City):
        self.city = city
        self.speed = city.max_v

    def add(self, passenger:Passenger):
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan": 
            # path info is stored as tuple ((x, y), position_type) 
            # position_type 1 means passenger origin, 2 means passenger destination
            if len(self.passenger) == 0: 
                self.path1.insert(0, ((passenger.x, passenger.y), 1))
                self.path2.insert(0, ((passenger.dx, passenger.dy), 2))
            else:
                self.path2.insert(0, ((passenger.dx, passenger.dy), 2))
                self.path2.insert(0, ((passenger.x, passenger.y), 1))

        if self.city.type_name == "real-world":  
            dist1, path1 = self.city.dijkstra(self.link.origin.id, passenger.link.origin.id)
            dist2, path2 = self.city.dijkstra(passenger.link.origin.id, passenger.d_link.origin.id)
            if (dist1 == -1 or dist2 == -1):
                return False
            # assign current location to passenger and passenger origin to destination
            self.path1 = path1 
            self.path2 = path2
            self.start1 = True
        self.load += 1
        self.passenger.insert(0, passenger)
    
    def pick_up(self):
        self.passenger[0].status = 2
        self.passenger[0].t_s = self.clock

    def release(self):
        if self.path2[0][1] == 2:
            self.passenger[0].status = 3
            self.passenger[0].t_end = self.clock
            self.passenger.pop(0)
        self.path2.pop(0)
        self.load -= 1
        
    def assign(self, passenger:Passenger):
        self.add(passenger)
        passenger.status = 1
        self.freq += 1
        status_request = self.changeStatusTo(0)
        return status_request

    def in_service(self):
        self.pick_up()
        status_request = self.changeStatusTo(1)
        return status_request

    def idle(self):
        self.passenger[0].status = 3
        self.passenger[0].t_end = self.clock
        self.passenger.pop(0)
        self.load -= 1
        status_request = self.changeStatusTo(2)
        return status_request

    def interchanging(self):
        status_requst = self.changeStatusTo(3)
        return status_requst
    
    def interchanged(self):
        status_request = self.changeStatusTo(2)
        return status_request

    # swap with other vehicle
    def swap(self, veh):
        temp1, temp2, temp3, temp4, temp5 = self.passenger, self.path1, self.path2, self.start1, self.load
        self.passenger, self.path1, self.path2, self.start1, self.load = veh.passenger, veh.path1, veh.path2, veh.start1, veh.load
        veh.passenger, veh.path1, veh.path2, veh.start1, veh.load = temp1, temp2, temp3, temp4, temp5
        status1, status2 = self.status, veh.status
        request1, request2 = self.changeStatusTo(status2), veh.changeStatusTo(status1)
        return (request1, request2)
        
    def idle_pos(self):
        x, y = 0, 0
        x = self.even_space*round(self.x / self.even_space)
        y = self.even_space*round(self.y / self.even_space)
        if x == 0:
            x += self.even_space
        elif x == self.city.length:
            x -= self.even_space
        if y == 0:
            y += self.even_space
        elif y == self.city.length:
            y -= self.even_space
        return (x, y)

    def location(self):
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":  
            return (self.x, self.y)

        if self.city.type_name == "real-world":
            (x, y) = utils.location_helper(self.link, self.len)
            return (x, y)

    # move along the path and update the location of vehicle
    def move(self, dt):
        self.clock += dt
        if (self.status == 0):
            self.ta += dt
            self.dist_a += dt * self.speed 
        elif (self.status == 1):
            self.ts += dt
            self.dist_s += dt * self.speed

        # initialize the not-changing status
        status_request = (self.id, -1, -1)
        # Eulidean movement
        if self.city.type_name == "Euclidean":
            if self.status == 0:
                reached = self.move_Euclidean(dt, self.path1[0][0])
                if (reached):
                    status_request = self.in_service()
            elif self.status == 1:
                reached = self.move_Euclidean(dt, self.path2[0][0])
                if (reached):
                    status_request = self.idle()
            elif self.status == 2:
                reached = self.move_Euclidean(dt, self.idle_position)
            elif self.status == 3:
                reached = self.move_Euclidean(dt, self.idle_position)
                if (reached):
                    status_request = self.interchanged()

        elif self.city.type_name == "Manhattan":  
            if self.status == 0:
                reached = self.move_Manhattan(dt, self.path1[0][0])
                if (reached):
                    status_request = self.in_service()     
            elif self.status == 1:
                reached = self.move_Manhattan(dt, self.path2[0][0])
                if (reached):
                    if (len(self.passenger) == 1):
                        status_request = self.idle()
                    else:
                        if self.path2[0][1] == 1:
                            self.pick_up()
                        self.release()
            elif self.status == 2:
                reached = self.move_Manhattan(dt, self.idle_position)
            elif self.status == 3:
                reached = self.move_Manhattan(dt, self.idle_position)
                if (reached):
                    status_request = self.interchanged()

        elif self.city.type_name == "real-world":
            # determine the movement of first path
            if (self.status == 2):
                return status_request
            elif (self.start1):
                # edge case path1 length is 1
                if (len(self.path1) == 1):
                    # different direction 
                    if (self.link.id != self.passenger[0].link.id):
                        self.len -= dt * self.speed
                        if (self.len < 0):
                            self.len = 0
                            self.link = self.passenger[0].link
                            self.start1 = False
                    else: 
                        self.start1 = False
                    return status_request
                # general case same direction
                elif (self.link.id == self.city.map[self.path1[0], self.path1[1]]):
                    self.start1 = False
                    return status_request
                # general case different direction 
                else:
                    self.len -= dt * self.speed
                    if (self.len < 0):
                        self.len = 0
                        self.link = self.city.links[self.city.map[self.path1[0], self.path1[1]]]
                        self.start1 = False
                    return status_request
            
            elif len(self.path1) != 0:
                self.move_real_world(dt, self.path1, self.passenger[0].link, self.passenger[0].len)
                return status_request
            elif len(self.path2) != 0:
                status_request = self.in_service()
                if (len(self.path2) >= 2 and self.link.id != self.city.map[self.path2[0], self.path2[1]]):
                    self.len -= dt * self.speed
                    if (self.len < 0):
                        self.len = 0
                        self.link = self.city.links[self.city.map[self.path2[0], self.path2[1]]]
                else:   
                    reached = self.move_real_world(dt, self.path2, self.passenger[0].d_link, self.passenger[0].d_len)
                    if (reached):    
                        status_request = self.idle()
        return status_request