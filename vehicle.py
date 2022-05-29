from os import stat_result
import utils 
from passenger import Passenger
from city import City
from city import CityLink
import math
import random

class Vehicle:
    def __init__(self, vehicle_id:tuple, city:City):
        self.status_table = {0:"assigned", 1:"in_service", 2:"idle", 3:"interchanged"}
        self.id, self.city = vehicle_id, city
        self.clock = 0
        if city.type_name == "Euclidean" or city.type_name == "Manhattan":    
            self.x, self.y = utils.generate_location(city)
        if city.type_name == "real-world":
            self.link, self.len = utils.generate_location(city)
        # around 30 mph
        self.speed = city.max_v
        self.load = 0
        self.status = 2
        self.passenger = []
        # random position when idling
        self.idle_position = None
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
                self.path1.insert(0, ((passenger.ox, passenger.oy), 1))
                self.path2.insert(0, ((passenger.dx, passenger.dy), 2))
            else:
                self.path2.insert(0, ((passenger.dx, passenger.dy), 2))
                self.path2.insert(0, ((passenger.ox, passenger.oy), 1))

        if self.city.type_name == "real-world":  
            dist1, path1 = self.city.dijkstra(self.link.origin.id, passenger.o_link.origin.id)
            dist2, path2 = self.city.dijkstra(passenger.o_link.origin.id, passenger.d_link.origin.id)
            if (dist1 == -1 or dist2 == -1):
                return False
            # assign current location to passenger and passenger origin to destination
            self.path1 = path1 
            self.path2 = path2
            self.start1 = True
        self.load += 1
        self.passenger.insert(0, passenger)
    
    def pick_up(self):
        self.passenger[0].status = "picked up"
        self.passenger[0].t_s = self.clock

    def release(self):
        if self.path2[0][1] == 2:
            self.passenger.pop(0)
        self.path2.pop(0)
        self.load -= 1
        
    # change self status to new status, and also change the position in self fleet
    def changeStatusTo(self, new_status:int):
        old_status = self.status
        self.status = new_status
        return (self.id, old_status, new_status)

    def assign(self, passenger:Passenger):
        self.add(passenger)
        self.freq += 1
        status_request = self.changeStatusTo(0)
        return status_request

    def in_service(self):
        self.pick_up()
        status_request = self.changeStatusTo(1)
        return status_request

    def idle(self):
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

    def location(self):
        if self.city.type_name == "Euclidean" or self.city.type_name == "Manhattan":  
            return (self.x, self.y)

        if self.city.type_name == "real-world":
            x1, y1 = self.link.origin.x, self.link.origin.y
            x2, y2 = self.link.destination.x, self.link.destination.y
            x3, y3 = None, None
            if (x1 == x2):
                x3 = x1
                if (y1 < y2): y3 = y1 + self.len
                else: y3 = y1 - self.len
                return (x3, y3)
            k = (y2 - y1)/(x2 - x1)
            if (x1 < x2):
                x3 = x1 + self.len / self.link.length * abs(x2 - x1)
                y3 = y1 + k*(x3 - x1)
            if (x1 > x2):
                x3 = x1 - self.len / self.link.length * abs(x2 - x1)
                y3 = y1 + k*(x3 - x1)   
            return (x3, y3)

    def sign(self, num):
        return (num > 0) - (num < 0)

    # move from current position to destination [x, y] using Euclidean space
    # return true if the goal is reached
    def move_Euclidean(self, dt:float, dxy:list):
        dx, dy = dxy[0], dxy[1]
        if (self.x == dx and self.y == dy):
            return True
        if (self.x == dx):
            ydir = self.sign(dy-self.y)
            self.y += ydir * dt * self.speed
            self.y = ydir*min(ydir*self.y, ydir*dy)
            if (self.y == dy):
                return True
        else:
            xdir = self.sign(dx-self.x)
            ydir = self.sign(dy-self.y)
            alpha = math.atan(abs(self.y-dy)/abs(self.x-dx))            
            self.x += xdir*self.speed*dt*math.cos(alpha) 
            self.y += ydir*self.speed*dt*math.sin(alpha)
            self.x = xdir*min(xdir*self.x, xdir*dx)
            self.y = ydir*min(ydir*self.y, ydir*dy)
            if (self.y == dy):
                return True
        return False

    # move from origin (x, y) to destination (x, y) using Manhattan space
    def move_Manhattan(self, dt:float, dxy:list):
            dx, dy = dxy[0], dxy[1]
            xmove = random.randint(0, 1)
            # xmove = 1
            ymove = 1 - xmove
            if (self.x == dx):
                xmove, ymove = 0, 1
            elif (self.y == dy):
                xmove, ymove = 1, 0
            xdir = self.sign(dx-self.x)
            ydir = self.sign(dy-self.y)
            self.x += xdir * xmove* dt * self.speed
            self.y += ydir * ymove* dt * self.speed
            self.x = xdir*min(xdir*self.x, xdir*dx) if xdir != 0 else self.x
            self.y = ydir*min(ydir*self.y, ydir*dy) if ydir != 0 else self.y
            if (self.x == dx and self.y == dy):
                return True 
            return False

    def move_real_world(self, dt, path:list, dlink:CityLink, dlen:float):
        """
        Let the status of vehicle changed as time goes
        `dt`: time gap
        `path`: list of CityNodes
        `dlink`: the Citylink where destination is on  
        `dlen`: distance from destination Citylink 
        `return`: True if the goal is reached
        """
        # edge case last citylink
        if len(path) == 0:
            return True
        if len(path) == 1:
            temp = self.len + dt * self.speed
            # driving over destination
            if (temp >= dlen):
                path.pop(0)
                self.len = dlen
                return True
            else:
                self.len = temp
        else:
            self.len += dt * self.speed
            if (self.len > self.link.length):
                path.pop(0)
                if (len(path) == 1):
                    self.link = dlink
                    self.len = 0
                # id of next link  
                else:
                    next_id = self.city.map[path[0], path[1]]
                    self.link = self.city.links[next_id]
                    self.len = 0
        return False

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
                    if (self.link.id != self.passenger[0].o_link.id):
                        self.len -= dt * self.speed
                        if (self.len < 0):
                            self.len = 0
                            self.link = self.passenger[0].o_link
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
                self.move_real_world(dt, self.path1, self.passenger[0].o_link, self.passenger[0].o_len)
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