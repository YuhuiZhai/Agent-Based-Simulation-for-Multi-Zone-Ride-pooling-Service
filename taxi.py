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
        self.rng = np.random.default_rng(seed=np.random.randint(100))
        self.status_record = []
        # prev_dir stores the previous direction of movement, dir_dict stores available direction and prob
        # curr_dir stores the current direction of movement
        self.prev_dir, self.curr_dir = None, None
        self.turning_xy = None
        # the table of status and trip distance, when status changes, record the od of previous trip
        # first item means status, second item means expected OD, third item means the start point and end point of current status
        self.delivery_distance_table = [[self.taxi_status, [None, None], [self.location(), None]]]
        self.pax_record = set()
        
    # return current position
    def location(self):
        return (self.x, self.y)

    # helper function to compare the distance of passengers'destination relative to a position
    # p1 is assigned passenger, p2 is compared passenger (can be None)
    def dist_helper(self, pos:tuple, p1:Passenger, p2:Passenger):
        if p2 == None:
            return p1, p2
        if p1.target_zone.id == p2.target_zone.id:
            d1 = abs(p1.dx - pos[0]) + abs(p1.dy - pos[1])
            d2 = abs(p2.dx - pos[0]) + abs(p2.dy - pos[1])
        else:
            x0, y0 = self.zone.center
            x1, y1 = p1.target_zone.center
            x2, y2 = p2.target_zone.center           
            d1 = abs(x0 - x1) + abs(y0 - y1)
            d2 = abs(x0 - x2) + abs(y0 - y2)
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
        passenger.status, passenger.t_a = 1, self.clock
        self.turning_xy = None
        self.prev_dir, self.curr_dir = None, None
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        new_taxi_status = (s0, (s0, passenger), (s2, p2), (s3, p3))  
        new_group_status = (s0, s0, s2, s3) 
        self.update_taxi_status(new_taxi_status)
        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # pick up the assigned passenger
    def pickup(self):
        # taxi cannot pick up if no assigned passenger
        if self.taxi_status[1][0] != self.taxi_status[0]:
            print("Error in pickup")
            return
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        p1.status, p1.t_s = 2, self.clock
        pos = (self.x, self.y)
        self.turning_xy = None
        self.prev_dir, self.curr_dir = None, None
        pfirst, psecond = self.dist_helper(pos, p1, p2)
        if psecond != None:
            new_taxi_status = (p1.zone.id, (-1, None), (pfirst.target_zone.id, pfirst), (psecond.target_zone.id, psecond))
            new_group_status = (p1.zone.id, -1, pfirst.target_zone.id, psecond.target_zone.id)
        else:
            new_taxi_status = (p1.zone.id, (-1, None), (pfirst.target_zone.id, pfirst), (-1, None))    
            new_group_status = (p1.zone.id, -1, pfirst.target_zone.id, -1)
        self.update_taxi_status(new_taxi_status)
        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # after pickinig up the assigned passenger, taxi is delivering passenger who has the closest destination
    def deliver(self):
        # Taxi cannot deliver if there is another assignment or no passenger on board
        if self.taxi_status[1] != (-1, None) or self.taxi_status[2] == (-1, None):
            print("Error in deliver")
            return 
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status   
        p2.status, p2.t_end = 3, self.clock
        self.turning_xy = None
        self.prev_dir, self.curr_dir = None, None
        new_taxi_status = (s0, (s1, p1), (s3, p3), (-1, None))
        new_group_status = (s0, s1, s3, -1)
        self.update_taxi_status(new_taxi_status)
        status_request = self.changeStatusTo(new_group_status)
        return status_request
        
    # rebalance the idle vehicle to a new zone
    def rebalance(self, zone:Zone):
        # taxi rebalanced should be idle (i, -1, -1, -1)
        if self.status != (self.zone.id, -1, -1, -1):
            print("Error in rebalance status")
            return 
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        self.idle_position = zone.generate_location()
        new_taxi_status = (s0, (zone.id, None), (-1, None), (-1, None))
        new_group_status = (s0, zone.id, -1, -1)
        self.update_taxi_status(new_taxi_status)
        status_request = self.changeStatusTo(new_group_status)
        return status_request
    
    # make the taxi idle status
    def idle(self):
        self.idle_position = None
        self.turning_xy = None
        new_taxi_status = (self.zone.id, (-1, None), (-1, None), (-1, None))
        new_group_status = (self.zone.id, -1, -1, -1)
        self.update_taxi_status(new_taxi_status)
        status_request = self.changeStatusTo(new_group_status)
        return status_request

    # when taxi goes out of the boundary of zone, self.city will firstly be changed by self.changeCity()
    # status will then be updated
    def cross(self):
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        new_taxi_status = (self.zone.id, (s1, p1), (s2, p2), (s3, p3))
        new_group_status = (self.zone.id, s1, s2, s3)
        self.update_taxi_status(new_taxi_status)
        status_request = self.changeStatusTo(new_group_status)
        self.prev_dir = self.curr_dir
        self.curr_dir = None
        return status_request

    # enter a new zone
    def changeZone(self, new_zone:Zone):
        self.zone = new_zone
        self.speed = new_zone.max_v
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

    def choose_dir(self, target_zone:Zone):
        dir_list = self.valid_dir(target_zone)
        # only one valid direction
        if len(dir_list) == 1:
            chosen_dir = dir_list[0]
        # two valid directions
        else:
            dir1, dir2 = dir_list
            prob = self.city.prob_matrix[self.zone.id][target_zone.id]
            p1, p2 = prob[dir1], prob[dir2]
            p1, p2 = p1/(p1+p2), p2/(p1+p2)
            indicator = self.rng.random()
            if indicator <= p1:
                chosen_dir = dir1
            else:
                chosen_dir = dir2
        return chosen_dir

    # move from current location toward adjacent zone in the direction of: 
    # N:0, E:1, W:2, S:3 
    def move_adjacent(self, dt, dir:int, test_deliver=False):
        dir_map = {0:(0, 1), 1:(1, 0), 2:(-1, 0), 3:(0, -1)}

        # Case that taxi follows the same previous route or this is the first travel zone
        if dir == self.prev_dir or self.prev_dir == None: 
            self.x += dir_map[dir][0]*self.speed*dt
            self.y += dir_map[dir][1]*self.speed*dt
        
        # Case that taxi change the direction. Taxi will choose random point. 
        else: 
            (s0, (s1, p1), (s2, p2), (s3, p3)) = self.taxi_status
            if self.turning_xy == None:
                xlim0, ylim0 = None, None
                if p2 != None:
                    xlim0, ylim0 = [self.x, p2.dx], [self.y, p2.dy]
                    xlim0.sort(); ylim0.sort()
                xlim, ylim = None, None
                # if direction is North or South, choose the upper/lower region divided by y value 
                if dir == 0 or dir == 3: 
                    ylim = [self.y, self.zone.center[1] + dir_map[dir][1]*self.zone.length/2]
                elif dir == 1 or dir == 2: 
                    xlim = [self.x, self.zone.center[0] + dir_map[dir][0]*self.zone.length/2]
                zone_xlim, zone_ylim = self.zone.xyrange()
                if not test_deliver:
                    if xlim == None and zone_xlim[0] < p2.dx and p2.dx < zone_xlim[1]:
                        xlim = xlim0
                    if ylim == None and zone_ylim[0] < p2.dy and p2.dy < zone_ylim[1]:
                        ylim = ylim0
                    self.turning_xy = self.zone.generate_location(xlim=xlim, ylim=ylim)
                else:
                    if xlim == None and zone_xlim[0] < p2.dx and p2.dx < zone_xlim[1]:
                        self.turning_xy = (p2.dx, self.y)
                    if ylim == None and zone_ylim[0] < p2.dy and p2.dy < zone_ylim[1]:
                        self.turning_xy = (self.x, p2.dy)
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
    def move_toward(self, dt, target_zone:Zone, test_deliver=False):
        status_request = None
        # return true if it is already in the target zone
        if self.zone.id == target_zone.id:
            return True, status_request
       # when the taxi entering the zone for the first time, initialize the current travel direction
        if self.curr_dir == None:
            chosen_dir = self.choose_dir(target_zone)
            self.curr_dir = chosen_dir
        reached = self.move_adjacent(dt, self.curr_dir, test_deliver)
        if reached:
            new_zone = self.city.neighborZone(self.zone, self.curr_dir)
            self.changeZone(new_zone)
            status_request = self.cross()
        return reached, status_request

    # input are current status and trip information of previous status
    def get_deliver_index(self, prev_trip, curr_trip):
        def check_lateral_detour(loc1, loc2):
            if loc1[0] == loc2[0] or loc1[1] == loc2[1]:
                return False
            return True
        curr_status, [loc1, loc2], _ = curr_trip
        prev_status = prev_trip[0]
        (s0, (s1, p1), (s2, p2), (s3, p3)) = curr_status
        (p_s0, (p_s1, p_p1), (p_s2, p_p2), (p_s3, p_p3)) = prev_status
        idx1, idx2 = None, None
        # (i, 0, i, 0)
        if s0 == s2 and s1 == -1 and s3 == -1:
            idx1 = 0
            # Case 1 prev status (i, i, 0, 0), inflow pii00_i
            if p_s0 == s0 and p_s0 == p_s1 and p_s2 == -1: idx2 = 0
            # Case 2,3 prve status (j, 0, i, 0) inflow ci0i0
            elif p_s0 != s0 and p_s1 == -1 and p_s2 == s0: 
                # Case 2 there is no lateral detour
                if not check_lateral_detour(loc1, loc2): idx2 = 1
                # Case 3 there is lateral detour
                else: idx2 = 2
            # Case 4,5 prev status (i, 0, i, i), inflow d_i0ii
            elif p_s0 == s0 and p_s1 == -1 and p_s2 == p_s0 and p_s3 == p_s0: 
                # Get the origin and destination zone of passengers
                o1, d1 = p_p2.odzone()
                o2, d2 = p_p3.odzone()
                # Case 4 two intrazonal trips
                if o1 == s0 and o2 == s0 and d1 == s0 and d2 == s0: idx2 = 3 
                # Case 5 two interzonal trips
                elif o1 != s0 and o2 != s0 and d1 == s0 and d2 == s0: idx2 = 4
        # (i, 0, i, i)
        elif s0 == s2 and s2 == s3:
            idx1 = 1
            # Case 1 prev status (i, i, i, 0)
            if p_s0 == p_s1 and p_s1 == p_s2: idx2 = 0
            # Case 2,3 prev status (j, 0, i, i)
            elif p_s0 != s0 and p_s2 == s0 and p_s3 == s0:
                # Case 2 there is no lateral detour
                if not check_lateral_detour(loc1, loc2): idx2 = 1
                # Case 3 there is lateral detour
                else: idx2 = 2
        # (i, 0, j, 0)
        elif s0 != s2 and s1 == -1 and s2 != -1 and s3 == -1:
            idx1 = 2
            # Case 1 prev status (i, i, 0, 0)
            if p_s0 == s0 and p_s0 == p_s1 and p_s2 == -1 and p_s3 == -1: idx2 = 0
            # Case 2 prev status (k, 0, j, 0) and 
            elif p_s0 != s0 and p_s1 == -1 and p_s2 == s2 and p_s3 == -1: 
                # starting and ending points are on boundary, indicating the trip is intermediate
                o1, d1 = p_p2.odzone()
                if o1 != s0 and d1 != s0: idx2 = 1 
            # Case 3 prev status (i, 0, i, j)
            elif p_s0 == s0 and p_s1 == -1 and p_s2 == s0 and p_s3 != -1 and p_s3 != s0: idx2 = 2
        # (i, 0, i, j)
        elif s0 == s2 and s1 == -1 and s3 != s0 and s3 != -1:
            idx1 = 3
            # Case 1 prev status (i, i, i, 0)
            if p_s0 == s0 and p_s1 == p_s0 and p_s2 == p_s1: idx2 = 0
            # Case 2 prev status (i, i, j, 0)
            elif p_s0 == s0 and p_s1 == s0 and p_s2 != s0 and p_s2 != -1: idx2 = 1
            # Case 3 prev status (j, 0, i, k)
            elif p_s0 != s0 and p_s1 == -1 and p_s2 == s0 and p_s3 != s0 and p_s3 != -1: idx2 = 2
        # (i, 0, j, k)
        elif s1 == -1 and s2 != s0 and s2 != -1 and s3 != s0 and s3 != -1:
            idx1 = 4
            # Case 1 prev status (i, i, j, 0)
            if p_s0 == s0 and p_s1 == s0 and p_s2 != s0 and p_s2 != -1 and p_s3 == -1: idx2 = 0
        return idx1, idx2
    
    # get the average trip distance of this taxi
    def get_delivery_distance(self):
        def get_dist(loc1, loc2):
            dist = abs(loc1[0]-loc2[0]) + abs(loc1[1]-loc2[1])
            return dist
        def convert(taxi_status):
            (s0, (s1, p1), (s2, p2), (s3, p3))= taxi_status
            status = (s0, s1, s2, s3)
            return status
        prev_trip = None
        n = len(self.delivery_distance_table)
        idx_pair = [(0, i) for i in range(5)]
        for i in range(3): 
            for j in range(3):
                idx_pair.append((i+1, j))
        idx_pair.append((4, 0))
        # key is (idx1, idx2), value is [sum, count]
        avg_trip_table = [{i:[0, 0] for i in idx_pair} for j in range(self.city.n**2)] 
        trip_num_table = [{i:0 for i in idx_pair} for j in range(self.city.n**2)] 
        for i in range(n-1):
            prev_trip = self.delivery_distance_table[i-1]
            curr_trip = self.delivery_distance_table[i]
            taxi_status, [loc1, loc2], _ = curr_trip
            curr_status = convert(taxi_status)
            (s0, s1, s2, s3) = curr_status
            idx1, idx2 = self.get_deliver_index(prev_trip, curr_trip)
            if idx1 == None or idx2 == None:
                continue
            if loc1 == None: print(idx1, idx2)
            avg_trip_table[s0][(idx1, idx2)][0] += get_dist(loc1, loc2) 
            avg_trip_table[s0][(idx1, idx2)][1] += 1 
        for s0 in range(len(avg_trip_table)):
            for i in avg_trip_table[s0]:
                if avg_trip_table[s0][i][1] == 0: 
                    trip_num_table[s0][i] = 0
                    avg_trip_table[s0][i] = None
                else:
                    trip_num_table[s0][i] = avg_trip_table[s0][i][1]
                    avg_trip_table[s0][i] = avg_trip_table[s0][i][0]/avg_trip_table[s0][i][1]
        return avg_trip_table, trip_num_table

    # update new taxi status
    def update_taxi_status(self, new_taxi_status):
        if self.taxi_status == new_taxi_status:
            return 
        self.taxi_status = new_taxi_status
        s0, (s1, p1), (s2, p2), (s3, p3) = new_taxi_status
        self.status_record.append((s0, s1, s2, s3))
        self.delivery_distance_table[-1][2][1] = self.location()
        if self.clock > self.city.T/3:
            # p2 is the current pax to be delivered
            if p2 != None:
                expected_od = [None, None]
                dx, dy = p2.location()[1]
                xlim, ylim = self.zone.xyrange()
                # when the passenger is in the range of target zone 
                if xlim[0] < dx and dx < xlim[1] and ylim[0] < dy and dy < ylim[1]:
                    # real case OD pair
                    expected_od = [self.location(), p2.location()[1]]
                else: 
                    # special case, when the deliver point is outside of zone, find out the boundary point
                    if self.curr_dir == None:
                        chosen_dir = self.choose_dir(p2.target_zone)
                    else:
                        chosen_dir = self.curr_dir
                    boundary = {0:(self.x, ylim[1]), 1:(xlim[1], self.y), 2:(xlim[0], self.y), 3:(self.x, ylim[0])}
                    expected_od = [self.location(), boundary[chosen_dir]]
                curr_trip = [new_taxi_status, expected_od, [self.location(), None]]
                self.delivery_distance_table.append(curr_trip)
            else: 
                self.delivery_distance_table.append([new_taxi_status, [None, None], [self.location(), None]])
        return

    # get trip distance of different cases

    # movement function between zones
    def move(self, dt, test_deliver=False):
        self.clock += dt
        s0, (s1, p1), (s2, p2), (s3, p3) = self.taxi_status
        status_request = None

        # rebalance status and interzonal travel
        if s0 != s1 and s1 != -1 and p1 == None and s2 == -1 and s3 == -1:
            if self.idle_position == None:
                print("Error in rebalance")
            reached = self.move_Manhattan(dt, self.idle_position, r=True)
            if reached:
                self.zone = self.city.getZone(s1)
                status_request = self.idle()

        # assigned status
        elif s0 == s1 and p1 != None and s3 == -1:
            reached = self.move_Manhattan(dt, (p1.x, p1.y))
            if reached:
                status_request = self.pickup()

        # delivering status and interzonal travel
        elif s1 == -1 and s2 != -1 and s0 != s2:
            reached, status_request = self.move_toward(dt, p2.target_zone, test_deliver)

        # delivering status and intrazonal travel
        elif s1 == -1 and s2 != -1 and s0 == s2:
            if self.prev_dir == 0 or self.prev_dir == 3: xfirst = False
            else: xfirst = True 
            reached = self.move_Manhattan(dt, (p2.dx, p2.dy), xfirst)
            # reached = self.move_Manhattan(dt, (p2.dx, p2.dy), r=True)
            if reached:
                status_request = self.deliver()
        
        # no change in status
        if status_request == None:
            self.update_taxi_status(self.taxi_status)
        return status_request
        
   