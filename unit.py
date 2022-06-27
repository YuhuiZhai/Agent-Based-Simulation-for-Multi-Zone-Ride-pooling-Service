import utils 
from city import City
from city import CityLink
import math
import random

class Unit:
    def __init__(self, id, city:City, init_status):
        self.id, self.city = id, city
        self.clock = 0
        self.speed = city.max_v
        if city.type_name == "Euclidean" or city.type_name == "Manhattan":    
            self.x, self.y = utils.generate_location(city)
            self.idle_position = self.x, self.y
        if city.type_name == "real-world":
            self.link, self.len = utils.generate_location(city)
            self.idle_position = self.link, self.len
        self.status = init_status
    
    # change self status to new status, and also return message to upper level
    def changeStatusTo(self, new_status:int):
        old_status = self.status
        self.status = new_status
        return (self.id, old_status, new_status)
    
    def sign(self, num):
        return (num > 0) - (num < 0)
    
    # move from current position to destination (x, y) using Euclidean space
    # return true if the goal is reached
    def move_Euclidean(self, dt:float, dxy:tuple):
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
            # print(alpha)        
            self.x += xdir*self.speed*dt*math.cos(alpha) 
            self.y += ydir*self.speed*dt*math.sin(alpha)
            self.x = xdir*min(xdir*self.x, xdir*dx) if xdir != 0 else self.x
            self.y = ydir*min(ydir*self.y, ydir*dy) if ydir != 0 else self.y
            if (self.x == dx and self.y == dy):
                return True
        return False

    # move from origin (x, y) to destination (x, y) using Manhattan space
    def move_Manhattan(self, dt:float, dxy:tuple):
            dx, dy = dxy[0], dxy[1]
            # xmove = random.randint(0, 1)
            xmove = 1
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
    
    # move along the real-world route 
    # path is the route, dlink is the last cityNode's citylink, dlen is the last mile
    def move_real_world(self, dt, path:list, dlink:CityLink, dlen:float):
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
    
