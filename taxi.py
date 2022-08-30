from passenger import Passenger
from city import City
from city import Zone
from unit import Unit
import numpy as np

class Taxi(Unit):
    def __init__(self, vehicle_id:tuple, zone:Zone, city:City, init_status):
        # default init_status is (city.id, (-1, None), (-1, None), (-1, None))
        # different from status in fleet, passenger is combined to s2 and s3 for convenience
        super().__init__(vehicle_id, zone, init_status)
        self.taxi_status = (zone.id, (-1, None), (-1, None), (-1, None))
        self.load = 0
        self.city = city
        # prev_dir stores the previous direction of movement, dir_dict stores available direction and prob
        # curr_dir stores the current direction of movement
        self.prev_dir, self.curr_dir = None, None
        self.turning_xy = None
    
    # return current position
    def location(self):
        return (self.x, self.y)
        
    # helper function to compare the distance of passengers'destination relative to a position
    # p1 is assigned passenger, p2 is compared passenger (can be None)
    def dist_helper(self, pos:tuple, p1:Passenger, p2:Passenger):
        if p2 == None:
            return p1, p2
        d1 = abs(p1.dx - pos[0]) + abs(p1.dy - pos[1])
        d2 = abs(p2.dx - pos[0]) + abs(p2.dy - pos[1])
        if d1 < d2: 
            return p1, p2
        else:
            return p2, p1

    # assign a passenger to a vehicle
    def assign(self, passenger:Passenger):
        # Passenger cannot be assigned to a full capacity taxi. 
        if self.taxi_status[1] != (-1, None) or self.taxi_status[3] != (-1, None):
            print("Error in assignment")
            return 
        passenger.status = 1
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        self.taxi_status = (s0, (s0, passenger), (s2, p2), (s3, p3)) 
        new_group_status = (s0, s0, s2, s3)
        
        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # pick up the assigned passenger
    def pickup(self):
        # taxi cannot pick up if no assigned passenger
        if self.taxi_status[1][0] != self.taxi_status[0]:
            print("Error in pickup")
            return
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        p1.status = 2
        pos = (self.x, self.y)
        self.turning_xy = None
        pfirst, psecond = self.dist_helper(pos, p1, p2)
        if psecond != None:
            self.taxi_status = (p1.zone.id, (-1, None), (pfirst.target_zone.id, pfirst), (psecond.target_zone.id, psecond))
            new_group_status = (p1.zone.id, -1, pfirst.target_zone.id, psecond.target_zone.id)
        else:
            self.taxi_status = (p1.zone.id, (-1, None), (pfirst.target_zone.id, pfirst), (-1, None))    
            new_group_status = (p1.zone.id, -1, pfirst.target_zone.id, -1)
        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # after pickinig up the assigned passenger, taxi is delivering passenger who has the closest destination
    def deliver(self):
        # Taxi cannot deliver if there is another assignment or no passenger on board
        if self.taxi_status[1] != (-1, None) or self.taxi_status[2] == (-1, None):
            print("Error in deliver")
            return 
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status   
        p2.status = 3
        self.taxi_status = (s0, (s1, p1), (s3, p3), (-1, None))
        new_group_status = (s0, s1, s3, -1)
        status_request = self.changeStatusTo(new_group_status)
        return status_request
        
    # rebalance the idle vehicle to a new zone
    def rebalance(self, zone:Zone):
        # taxi rebalanced should be idle (i, -1, -1, -1)
        if self.taxi_status[1] != -1 or self.taxi_status[2] != (-1, None):
            print("Error in rebalance")
            return 
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        self.taxi_status = (s0, (zone.id, None), (-1, None), (-1, None))
        new_group_status = (s0, zone.id, -1, -1)
        status_request = self.changeStatusTo(new_group_status)
        return status_request
    
    # make the taxi idle status
    def idle(self):
        self.taxi_status = (self.zone.id, (-1, None), (-1, None), (-1, None))
        new_group_status = (self.zone.id, -1, -1, -1)
        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # when taxi goes out of the boundary of zone, self.city will firstly be changed by self.changeCity()
    # status will then be updated
    def cross(self):
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        self.taxi_status = (self.zone.id, (s1, p1), (s2, p2), (s3, p3))
        new_group_status = (self.zone.id, s1, s2, s3)

        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # enter a new zone
    def changeZone(self, new_zone:Zone):
        self.zone = new_zone
        self.speed = new_zone.max_v
        self.prev_dir = self.curr_dir
        self.curr_dir = None
        self.turning_xy = None
        return 

    # given current zone and target zone, return valid direction in list
    def valid_dir(self, target_zone:Zone):
        curr_i, curr_j = self.zone.ij
        target_i, target_j = target_zone.ij
        if curr_i == target_i and curr_j == target_j:
            print("Error in movement")  
            return    
        dir_list = []
        # taxi should move North
        if curr_i > target_i: dir_list.append(0)
        # taxi should move South
        elif curr_i < target_i: dir_list.append(3)
        # taxi should move West
        if curr_j > target_j: dir_list.append(2)
        # taxi should move Eest
        elif curr_j < target_j: dir_list.append(1)
        return dir_list

    # move from current location toward adjacent zone in the direction of: 
    # N:0, E:1, W:2, S:3 
    def move_adjacent(self, dt, dir:int):
        dir_map = {0:(0, 1), 1:(1, 0), 2:(-1, 0), 3:(0, -1)}

        # Case that taxi follows the same previous route or this is the first travel zone
        if dir == self.prev_dir or self.prev_dir == None: 
            self.x += dir_map[dir][0]*self.speed*dt
            self.y += dir_map[dir][1]*self.speed*dt
        
        # Case that taxi change the direction. Taxi will choose random point. 
        else: 
            if self.turning_xy == None:
                xlim, ylim = None, None
                # if direction is North or South, choose the upper/lower region divided by y value 
                if dir == 0 or dir == 3: 
                    ylim = [self.y, self.zone.center[1] + dir_map[dir][1]*self.zone.length/2]
                elif dir == 1 or dir == 2: 
                    xlim = [self.x, self.zone.center[0] + dir_map[dir][0]*self.zone.length/2]
                self.turning_xy = self.zone.generate_location(xlim=xlim, ylim=ylim)
            if dir == 0 or dir == 3: xfirst = True
            else: xfirst = False 
            reached = self.move_Manhattan(dt, self.turning_xy, xfirst)
            if reached:
                self.prev_dir = dir
            return False

        # if one taxi is out of boundary, drag it back to the edge of zone 
        out_of_boundary, out_dir = self.out_of_boundary()
        if out_of_boundary:
            if out_dir == 0:
                self.x = self.zone.center[0] + dir_map[dir][0]*self.zone.length/2
            else:
                self.y = self.zone.center[1] + dir_map[dir][1]*self.zone.length/2
            return True
        return False
    
    # move from current toward target zone
    def move_toward(self, dt, target_zone:Zone):
        status_request = None
        # return true if it is already in the target zone
        if self.zone.id == target_zone.id:
            return True, status_request
       # when the taxi entering the zone for the first time, initialize the current travel direction
        if self.curr_dir == None:
            dir_list = self.valid_dir(target_zone)
            # only one valid direction
            if len(dir_list) == 1:
                chosen_dir = dir_list[0]
            # two valid directions
            else:
                dir1, dir2 = dir_list
                p1, p2 = self.zone.prob[dir1], self.zone.prob[dir2]
                p1, p2 = p1/(p1+p2), p2/(p1+p2)
                indicator = np.random.random()
                if indicator <= p1:
                    chosen_dir = dir1
                else:
                    chosen_dir = dir2
            self.curr_dir = chosen_dir
        reached = self.move_adjacent(dt, self.curr_dir)
        if reached:
            new_zone = self.city.neighborZone(self.zone, self.curr_dir)
            self.changeZone(new_zone)
            status_request = self.cross()
        return False, status_request


    # movement function between zones
    def move(self, dt):
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        status_request = None
        # idle status
        if s1 == -1 and s2 == -1 and s3 == -1:
            return status_request
        # rebalance status and interzonal travel
        if s1 != -1 and s0 != s1 and s2 == -1 and s3 == -1:
            reached, status_request = self.move_toward(p1)
            return status_request 

        # rebalance status and intrazonal travel
        if s1 != -1 and s0 == s1 and p1 == None and s2 == -1 and s3 == -1:
            if self.idle_position == None:
                self.idle_position = self.zone.generate_location()
            reached = self.move_Manhattan(dt, self.idle_position)
            if reached:
                status_request = self.idle()
            return status_request 

        # assigned status
        if s0 == s1 and p1 != None and s3 == -1:
            reached = self.move_Manhattan(dt, (p1.x, p1.y))
            if reached:
                status_request = self.pickup()
            return status_request

        # delivering status and interzonal travel
        if s1 == -1 and s2 != -1 and s0 != s2:
            reached, status_request = self.move_toward(dt, p2.target_zone)
            return status_request

        # delivering status and intrazonal travel
        if s1 == -1 and s2 != -1 and s0 == s2:
            reached = self.move_Manhattan(dt, (p2.dx, p2.dy))
            if reached:
                status_request = self.deliver()
            return status_request
            
    def print(self):
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        print(f"status {s0, s1, s2, s3}, pos {(self.x, self.y)};")