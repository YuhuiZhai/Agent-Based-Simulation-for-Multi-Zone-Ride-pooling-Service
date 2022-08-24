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
            self.x, self.y = self.city.generate_location()
            self.idle_position = self.x, self.y
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
    