from fleet import Fleet
from city import City
from taxi import Taxi
from passenger import Passenger
import numpy as np

class Taxifleet(Fleet):
    def __init__(self, fleet_m, id, city:City, T, rebalance_m=None):
        super().__init__(id)    
        self.city, self.T, self.rebalance_m  = city, T, rebalance_m
        self.rng = np.random.default_rng(seed=np.random.randint(100))
        n = len(fleet_m)
        if n != city.n:
            print("Error in matrix dimension")
            return     
        self.zone_group = {}
        for i in range(city.n**2):
            self.zone_group[i] = {}
        # assign taxi to each zone
        for i in range(n):
            for j in range(n):
                fleet_size = fleet_m[i][j]
                zone = city.zone_matrix[i][j]
                idle_status = (zone.id, -1, -1, -1)
                self.addVehGroup(idle_status)
                self.zone_group[zone.id][(-1, -1, -1)] = set()
                for k in range(fleet_size):
                    veh = Taxi((zone.id, k), zone, city, idle_status)
                    self.vehicles[veh.id] = veh 
                    self.vehs_group[idle_status].add(veh)
                    self.zone_group[zone.id][(-1, -1, -1)].add(veh)
        self.init_rebalance()
        self.valid_i0i0s_1 = {i:[] for i in range(self.city.n**2)}
        self.valid_i0i0s_4 = {i:[] for i in range(self.city.n**2)}
        self.valid_i0i0s_4_diag = {i:[] for i in range(self.city.n**2)}
        self.test = []
        

    # zone_move() replaces default move() 
    def zone_move(self, dt):
        for id in self.vehicles:
            status_request = self.vehicles[id].move(dt)
            self.changeVehStatus(status_request)
            self.changeZoneStatus(status_request)
        self.clock += dt
        return 
    
    def count(self, status:tuple):
        if status not in self.vehs_group:
            return -1
        return len(self.vehs_group[status])

    # change veh's status from status1 to status2 
    # the input is the same as changeVehStatus
    def changeZoneStatus(self, status_request:tuple):
        if status_request == None:
            return 
        veh_id, status1, status2 = status_request
        if status1 == status2:
            return
        # split the status (s0, s1, s2, s3) into s0, (s1, s2, s3)
        i, status1 = status1[0], (status1[1], status1[2], status1[3])
        j, status2 = status2[0], (status2[1], status2[2], status2[3])
        veh = self.vehicles[veh_id]
        if status2 not in self.zone_group[j]:
            self.zone_group[j][status2] = set() 
        set_out, set_in = self.zone_group[i][status1], self.zone_group[j][status2]
        set_out.remove(veh)
        set_in.add(veh)
        return 

    # dist_type is [1: assigned distance, 2: service distance, 3:total distance]
    def dist(self, vehicle:Taxi, passenger:Passenger, dist_type:int):
        i_table = {1:[1, 0], 2:[0, 1], 3:[1, 1]} 
        i1, i2 = i_table[dist_type]
        dist = i1*(abs(vehicle.x - passenger.x) + abs(vehicle.y - passenger.y)) \
            +  i2*(abs(passenger.x - passenger.dx) + abs(passenger.y - passenger.dy))
        return dist
    
    # convert status (s0, s1, s2, s3) to 0/1/2/3 (idle/assigned/in service/rebalancing)
    def convertStatus(self, taxi_status):
        (s0, (s1, p1), (s2, p2), (s3, p3)) = taxi_status
        # idle status
        if s1 == -1 and s2 == -1 and s3 == -1:
            return 0
        # assigned status
        if s0 == s1 and p1 != None:
            return 1
        # in service status
        if s1 == -1 and s2 != -1:        
            return 2
        # rebalance status
        if s0 != s1 and p1 == None:
            return 3
        
    # function to return location of each status group
    def sketch_helper(self):
        # key is status, value is location list
        sketch_table = []
        for status in range(4):
            sketch_table.append([[], []])
        for veh_id in self.vehicles:
            veh = self.vehicles[veh_id]
            taxi_status = veh.taxi_status
            converted = self.convertStatus(taxi_status)
            sketch_table[converted][0].append(veh.location()[0])
            sketch_table[converted][1].append(veh.location()[1])
        return sketch_table

    # initialization for rebalance 
    # the pattern of rebalance_m should be:
    #        [[b00, b01, ... b0k]
    #          ...           ...
    #         [bk0, bk1, ... bkk]
    def init_rebalance(self):
        if self.rebalance_m == None:
            return 
        # rebalance_info stores [(time to rebalance, origin i, destination j)]  
        self.rebalance_info = []
        self.rebalance_idx = 0
        for i in range(len(self.rebalance_m)):
            for j in range(len(self.rebalance_m[i])):
                if i == j:
                    continue
                t = 0
                bij = self.rebalance_m[i][j]
                if bij == 0:
                    continue
                while t < self.T:
                    dt = self.rng.exponential(scale=1/bij)
                    t += dt
                    self.rebalance_info.append((t, i, j))
        self.rebalance_info.sort(key=lambda k : k[0])
        return 

    # rebalance idle taxi according to the rebalance matrix
    def rebalance(self):
        t, i, j = self.rebalance_info[self.rebalance_idx]
        while t <= self.clock:
            if self.rebalance_idx >= len(self.rebalance_info):
                return 
            idle_group = self.zone_group[i][(-1, -1, -1)]
            for idle_taxi in idle_group:
                status_request = idle_taxi.rebalance(self.city.getZone(j))
                self.changeVehStatus(status_request)
                self.changeZoneStatus(status_request)
                break
            self.rebalance_idx += 1
            t, i, j = self.rebalance_info[self.rebalance_idx]
        return 


    # sevre a passenger by assigning the closet feasible taxi 
    def serve(self, passenger:Passenger):
        c_oxy, c_dxy = passenger.location()
        ozone, dzone = passenger.zone, passenger.target_zone
        opt_veh, opt_dist = None, None
        dist_info = [0, 0, 0, 0, 0]
        # intrazonal caller
        if ozone.id == dzone.id:
            xlim1, ylim1, xlim2, ylim2 = self.city.feasibleZone_1(c_oxy, c_dxy, ozone.id)
            fz = self.city.feasibleZone_3(c_oxy, c_dxy, ozone.id)
            opt_veh0, opt_veh1, opt_veh3 = None, None, None
            dist0, dist1, dist3 = 2*self.city.length, 2*self.city.length, 2*self.city.length
            for status in self.zone_group[ozone.id]:
                (s1, s2, s3) = status
                # idle veh 
                if s1 == -1 and s2 == -1 and s3 == -1:
                    for idle_veh in self.zone_group[ozone.id][status]:
                        dist = self.dist(idle_veh, passenger, 1)
                        if dist < dist0:
                            opt_veh0, dist0 = idle_veh, dist

                # delivering status with one pax 
                if s1 == -1 and s2 != -1 and s3 == -1:
                    # suitable ni0i0 number
                    valid_i0i0 = 0
                    temp = [(passenger.x, passenger.y), (passenger.dx, passenger.dy), (xlim1, ylim1), (xlim2, ylim2)]
                    for veh in self.zone_group[ozone.id][status]:
                        p2 = veh.taxi_status[2][1]
                        pdx, pdy = p2.dx, p2.dy
                        # feasible zone of Case 1 intra intra (p v)
                        if (ozone.id == s2):
                            if ((xlim1[0] <= pdx and pdx <= xlim1[1] and ylim1[0] <= pdy and pdy <= ylim1[1]) or\
                                (xlim2[0] <= pdx and pdx <= xlim2[1] and ylim2[0] <= pdy and pdy <= ylim2[1])):  
                                dist = self.dist(veh, passenger, 1)
                                valid_i0i0 += 1
                                if dist < dist1:
                                    opt_veh1, dist1 = veh, dist
                            else:
                                temp.append((pdx, pdy))
                        # feasible zone of Case 3 intra inter (p v)
                        elif ozone.id != s2 and s2 in fz:
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist3:
                                opt_veh3, dist3 = veh, dist
                    if ozone.id == 2 and valid_i0i0 == 0:
                        self.test.append(temp)
                    if ozone.id == s2:
                        self.valid_i0i0s_1[ozone.id].append([valid_i0i0, self.count((ozone.id, -1, ozone.id, -1))])
            dist_info[0] = dist0 if dist0 != 2*self.city.length else 0
            dist_info[1] = dist1 if dist1 != 2*self.city.length else 0
            dist_info[3] = dist3 if dist3 != 2*self.city.length else 0
        
            opt_veh, opt_dist = min([(opt_veh0, dist0), (opt_veh1, dist1), (opt_veh3, dist3)], key=lambda k : k[1])
        else:
            fz = self.city.feasibleZone_2(ozone.id, dzone.id)
            xlim, ylim, diag = self.city.feasibleZone_4(c_oxy, ozone.id, dzone.id)
            opt_veh0, opt_veh2, opt_veh4 = None, None, None
            dist0, dist2, dist4 = 2*self.city.length, 2*self.city.length, 2*self.city.length
            for status in self.zone_group[ozone.id]:
                (s1, s2, s3) = status
                # idle veh 
                if s1 == -1 and s2 == -1 and s3 == -1:
                    for idle_veh in self.zone_group[ozone.id][status]:
                        dist = self.dist(idle_veh, passenger, 1)
                        if dist < dist0:
                            opt_veh0, dist0 = idle_veh, dist

                elif s1 == -1 and s2 != -1 and s3 == -1:
                    valid_i0i0 = 0
                    valid_i0i0_diag = 0
                    for veh in self.zone_group[ozone.id][status]:
                        p2 = veh.taxi_status[2][1]
                        pdx, pdy = p2.dx, p2.dy
                        # feasible zone of Case 2 inter inter (p v)
                        if ozone.id != s2 and s2 in fz:  
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist2:
                                opt_veh2, dist2 = veh, dist
                        # feasible zone of Case 4 inter intra (p v)
                        elif ozone.id == s2 and \
                            (xlim[0] <= pdx and pdx <= xlim[1] and ylim[0] <= pdy and pdy <= ylim[1]):
                            if diag: valid_i0i0_diag += 1
                            else: valid_i0i0 += 1
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist4:
                                opt_veh4, dist4 = veh, dist
                    if ozone.id == s2:
                        self.valid_i0i0s_4[ozone.id].append([valid_i0i0, self.count((ozone.id, -1, ozone.id, -1))])
                        self.valid_i0i0s_4_diag[ozone.id].append([valid_i0i0_diag, self.count((ozone.id, -1, ozone.id, -1))])

            dist_info[0] = dist0 if dist0 != 2*self.city.length else 0
            dist_info[2] = dist2 if dist2 != 2*self.city.length else 0
            dist_info[4] = dist4 if dist4 != 2*self.city.length else 0
            opt_veh, opt_dist = min([(opt_veh0, dist0), (opt_veh2, dist2), (opt_veh4, dist4)], key=lambda k : k[1])
            
        if opt_veh == None:
            passenger.status = -1
            return opt_veh, opt_dist, None
        if opt_veh == opt_veh0:
            passenger.rs_status = 0
        else: passenger.rs_status = 1
        prev_status = opt_veh.status 
        passenger.update_dist_info(dist_info)
        status_request = opt_veh.assign(passenger)
        self.changeVehStatus(status_request)
        self.changeZoneStatus(status_request)
        return opt_veh, opt_dist, prev_status
