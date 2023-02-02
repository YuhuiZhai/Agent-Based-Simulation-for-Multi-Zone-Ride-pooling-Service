from city import Zone
import random

class Unit:
    def __init__(self, id, zone:Zone, init_status):
        self.clock, self.id, self.zone = 0, id, zone
        self.speed = zone.max_v
        self.x, self.y = self.zone.generate_location()
        self.idle_position = None
        self.status = init_status
        self.prev_status = None
        # every taxi's status is restricted to change at most once at a time
        self.status_transition_count = 0

    # change self status to new status, and also return message to upper level
    def changeStatusTo(self, new_status):
        if self.status_transition_count > 1:
            print("Error in transfer")
            return 
        old_status = self.status
        self.status = new_status
        self.status_transition_count = 0
        return (self.id, old_status, new_status)
        
    # check the sign
    def sign(self, num):
        num = float(num)
        return (num > 0) - (num < 0)

    # move from origin (x, y) to destination (x, y) using Manhattan space
    def move_Manhattan(self, dt:float, dxy:tuple, xfirst=True, r=False):
        dx, dy = dxy[0], dxy[1]
        xmove = xfirst
        if r:
            xmove = random.randint(0, 1)    
        ymove = 1 - xmove
        if (self.x == dx and self.y == dy):
            xmove, ymove = 0, 0
        elif (self.y == dy):
            xmove, ymove = 1, 0
        elif (self.x == dx):
            xmove, ymove = 0, 1
        xdir = self.sign(dx-self.x)
        ydir = self.sign(dy-self.y)
        self.x += xdir * xmove* dt * self.speed
        self.y += ydir * ymove* dt * self.speed
        self.x = xdir*min(xdir*self.x, xdir*dx) if xdir != 0 else self.x
        self.y = ydir*min(ydir*self.y, ydir*dy) if ydir != 0 else self.y
        if (self.x == dx and self.y == dy):
            return True 
        return False
    
    # return whether one unit is out of boundary and which direction is out of boundary
    def out_of_boundary(self):
        xout = (abs(self.x - self.zone.center[0]) >= (self.zone.length/2))
        yout = (abs(self.y - self.zone.center[1]) >= (self.zone.length/2))
        out_dir = None
        if xout: out_dir = 0
        elif yout: out_dir = 1
        return xout or yout, out_dir
    
    def valid_trans(self):
        return self.status_transition_count == 0
    