from fleet import Fleet
from city import City
from taxi import Taxi
from passenger import Passenger
import numpy as np
import pyomo
import pyomo.opt
import pyomo.environ as pe
class Taxifleet(Fleet):
    def __init__(self, fleet_m, id, city:City, dt, T, rebalance_m=None, turning_random=True):
        super().__init__(id)    
        self.fleet_m, self.city, self.dt, self.T, self.rebalance_m, self.turning_random  = fleet_m, city, dt, T, rebalance_m, turning_random
        self.rng = np.random.default_rng(seed=np.random.randint(100))
        self.assigned_num_tp = [0, 0, 0, 0]
        self.init_taxi()
        self.init_rebalance()
    
    # initialization of taxis
    def init_taxi(self):
        n = len(self.fleet_m)
        self.zone_group = {}
        for i in range(self.city.n**2):
            self.zone_group[i] = {}
        # assign taxi to each zone
        for i in range(n):
            for j in range(n):
                fleet_size = int(self.fleet_m[i][j])
                zone = self.city.zone_matrix[i][j]
                idle_status = (zone.id, -1, -1, -1)
                self.addVehGroup(idle_status)
                self.zone_group[zone.id][(-1, -1, -1)] = set()
                for k in range(fleet_size):
                    veh = Taxi((zone.id, k), zone, self.city, idle_status, turning_random=self.turning_random)
                    self.vehicles[veh.id] = veh 
                    self.vehs_group[idle_status].add(veh)
                    self.zone_group[zone.id][(-1, -1, -1)].add(veh)
        return 

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

    # fleet_move() replaces default move() 
    def fleet_move(self, dt, test_deliver=False):
        for id in self.vehicles:
            status_request = self.vehicles[id].move(dt, test_deliver)
            self.changeVehStatus(status_request)
            self.changeZoneStatus(status_request)
        self.clock += dt
        self.assigned_num_tp = [0, 0, 0, 0]
        return 
    
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

    # rebalance idle taxi according to the rebalance matrix
    def rebalance(self):
        if self.rebalance_m == None:
            return 
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
    
    def extra_rebalance(self, bound_m):
        for i in range(self.city.n**2):
            rebalance_num = 0
            for j in range(self.city.n**2):
                if j == i: continue
                if (i, -1, -1) in self.zone_group[j]:
                    rebalance_num += len(self.zone_group[j][(i, -1, -1)])
            for j in range(self.city.n**2):
                if i == j: continue
                idle_num = len(self.zone_group[i][(-1, -1, -1)])
                if idle_num + rebalance_num <= bound_m[i][0]:
                    idle_taxis_j = self.zone_group[j][(-1, -1, -1)]
                    if len(idle_taxis_j) >= bound_m[j][0]:
                        for veh in idle_taxis_j:
                            if not veh.valid_trans():
                                continue
                            status_request = veh.rebalance(self.city.getZone(i))
                            self.changeVehStatus(status_request)
                            self.changeZoneStatus(status_request)
                            break
        return 

    def rebalance_tp(self):
        def get_ni000(i):
            idle_num = len(self.zone_group[i][(-1, -1, -1)])
            rebalance_num = 0
            for i in range(self.city.n**2):
                for j in range(self.city.n**2):
                    if i == j: continue
                    if (i, -1, -1) in self.zone_group[j]: rebalance_num += len(self.zone_group[j][(i, -1, -1)])
            assigned_num_tp = self.assigned_num_tp[i]
            return idle_num - assigned_num_tp
        all_pos, all_neg = True, True
        b = [0 for i in range(self.city.n**2)]
        sum_supply, sum_demand = 0, 0
        for i in range(self.city.n**2):
            ni000 = get_ni000(i)
            pos, neg = ni000 > 0, ni000 < 0
            all_pos = all_pos and pos
            all_neg = all_neg and neg
            if pos: sum_supply += ni000
            if neg: sum_demand += ni000
            b[i] = ni000
        if all_pos or all_neg: return np.zeros((self.city.n**2, self.city.n**2)), b
        sd = b
        A = min(sum_supply, abs(sum_demand))
        for i in range(len(b)): 
            if b[i] > 0: b[i] = b[i] * min(A / sum_supply, 1)
            if b[i] < 0: b[i] = b[i] * min(abs(A / sum_demand), 1)
        rebalance_m = self.rebalance_tp_helper(b)
        for i in range(self.city.n**2):
            for j in range(self.city.n**2):
                if i == j: continue
                num = 0
                while num < rebalance_m[i][j]:
                    taxi = None
                    for idle_taxi in self.zone_group[i][(-1, -1, -1)]:
                        if not idle_taxi.valid_trans(): continue
                        num += 1
                        taxi = idle_taxi
                        scan_all = False
                        break
                    if taxi == None: break
                    status_request = taxi.rebalance(self.city.getZone(j))
                    self.changeVehStatus(status_request)
                    self.changeZoneStatus(status_request) 
        return np.array(rebalance_m), sd

    def rebalance_tp_helper(self, b):
        # Build a model
        m = pe.ConcreteModel()

        # Declare the decision variable -- how many vehicles to be rebalanced between zone i to zone j, self.all_zone is a list of zone index, e.g., [0, 1, 2, 3]
        self.all_zone = [i for i in range(self.city.n**2)]
        m.x = pe.Var(self.all_zone, self.all_zone, domain = pe.NonNegativeReals)

        # Declare the objective function -- self.Dist[i,j]*self.phi is the distance between zone i's center and zone j's center, self.v is the speed
        Dist = [[10000 for i in range(self.city.n**2)] for j in range(self.city.n**2)] 
        for i in range(self.city.n**2):
            for j in range(self.city.n**2):
                if i == j: continue
                Dist[i][j] = self.city.dist_btw(i, j)

        m.Cost = pe.Objective(expr = sum([Dist[i][j]/self.city.max_v*m.x[i,j] for i in self.all_zone for j in self.all_zone]), sense = pe.minimize)

        # Declare the constraints -- the number of vehicles out of a zone minue the number of vehicles into a zone should be equal to the number of vehicles to be rebalanced out of zone i (represented by self.b[i])
        m.constraints = pe.ConstraintList()
        for i in self.all_zone:
            m.constraints.add(sum([m.x[i,j] for j in self.all_zone]) - sum([m.x[j,i] for j in self.all_zone]) == b[i])

        # Solve the problem
        pe.SolverFactory('glpk').solve(m)

        # Get the value of decision variable x_ij
        rebalance_m = [[0 for j in range(self.city.n**2)] for i in range(self.city.n**2)]
        for i, j in m.x:
            rebalance_m[i][j] = int(m.x[i, j].value)
        return rebalance_m

    def computeP(self):
        P = 0
        for i in range(self.city.n**2):
            ii00, i0i0, iii0, i0ii = (i,i,-1,-1), (i,-1,i,-1), (i,i,i,-1), (i,-1,i,i)
            nii00 = self.count(ii00) if self.count(ii00) != -1 else 0
            ni0i0 = self.count(i0i0) if self.count(i0i0) != -1 else 0
            niii0 = self.count(iii0) if self.count(iii0) != -1 else 0
            ni0ii = self.count(i0ii) if self.count(i0ii) != -1 else 0
            P += nii00 + ni0i0 + 2*(niii0 + ni0ii)
            for j in range(self.city.n**2):
                if j == i: 
                    continue
                i0j0, i0ij, iij0 = (i,-1,j,-1), (i,-1,i,j), (i,i,j,-1)
                ni0j0 = self.count(i0j0) if self.count(i0j0) != -1 else 0
                ni0ij = self.count(i0ij) if self.count(i0ij) != -1 else 0
                niij0 = self.count(iij0) if self.count(iij0) != -1 else 0
                omegaij = self.city.omega(i, j)
                P += ni0j0 + 2*ni0ij + 2*niij0
                for k in omegaij:
                    i0jk = (i,-1,j,k) 
                    ni0jk = self.count(i0jk) if self.count(i0jk) != -1 else 0
                    P += 2*ni0jk
        return P

    def sign(self, num):
        num = float(num)
        return (num > 0) - (num < 0)
    
    def count(self, status:tuple):
        if status not in self.vehs_group:
            return -1
        return len(self.vehs_group[status])

    # sevre a passenger by assigning the closet feasible taxi 
    def serve(self, passenger:Passenger):
        c_oxy, c_dxy = passenger.location()
        o_id, d_id = passenger.odzone()
        self.assigned_num_tp[o_id] += 1
        opt_veh, opt_dist = None, None
        # intrazonal caller
        if o_id == d_id:
            xlim1, ylim1, xlim2, ylim2 = self.city.feasibleZone_1(c_oxy, c_dxy, o_id)
            fz = self.city.feasibleZone_3(c_oxy, c_dxy, o_id)
            opt_veh0, opt_veh1, opt_veh3 = None, None, None
            dist0, dist1, dist3 = 2*self.city.length, 2*self.city.length, 2*self.city.length
            for status in self.zone_group[o_id]:
                (s1, s2, s3) = status
                # idle veh 
                if s1 == -1 and s2 == -1 and s3 == -1:
                    for idle_veh in self.zone_group[o_id][status]:
                        if not idle_veh.valid_trans():
                            continue
                        dist = self.dist(idle_veh, passenger, 1)
                        if dist < dist0:
                            opt_veh0, dist0 = idle_veh, dist
                # delivering status with one pax 
                if s1 == -1 and s2 != -1 and s3 == -1:
                    for veh in self.zone_group[o_id][status]:
                        p2 = veh.taxi_status[2][1]
                        pdx, pdy = p2.location()[1]
                        # feasible zone of Case 1 intra intra (p v)
                        if not veh.valid_trans():
                            continue 
                        if (o_id == s2):
                            if ((xlim1[0] <= pdx and pdx <= xlim1[1] and ylim1[0] <= pdy and pdy <= ylim1[1]) or\
                                (xlim2[0] <= pdx and pdx <= xlim2[1] and ylim2[0] <= pdy and pdy <= ylim2[1])): 
                                
                                dist = self.dist(veh, passenger, 1)
                                if dist < dist1:
                                    opt_veh1, dist1 = veh, dist
                        # feasible zone of Case 3 intra inter (p v)
                        elif o_id != s2 and s2 in fz:
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist3:
                                opt_veh3, dist3 = veh, dist
        
            opt_veh, opt_dist = min([(opt_veh0, dist0), (opt_veh1, dist1), (opt_veh3, dist3)], key=lambda k : k[1])
        # interzonal caller
        else:
            fz = self.city.feasibleZone_2(o_id, d_id)
            xlim, ylim, diag = self.city.feasibleZone_4(c_oxy, o_id, d_id)
            opt_veh0, opt_veh2, opt_veh4 = None, None, None
            dist0, dist2, dist4 = 2*self.city.length, 2*self.city.length, 2*self.city.length
            for status in self.zone_group[o_id]:
                (s1, s2, s3) = status
                # idle veh 
                if s1 == -1 and s2 == -1 and s3 == -1:
                    for idle_veh in self.zone_group[o_id][status]:
                        if not idle_veh.valid_trans():
                            continue 
                        dist = self.dist(idle_veh, passenger, 1)
                        if dist < dist0:
                            opt_veh0, dist0 = idle_veh, dist

                elif s1 == -1 and s2 != -1 and s2 != o_id and s3 == -1:
                    for veh in self.zone_group[o_id][status]:
                        if not veh.valid_trans():
                            continue 
                        # feasible zone of Case 2 inter inter (p v)
                        if s2 in fz:  
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist2:
                                opt_veh2, dist2 = veh, dist

                elif s1 == -1 and s2 == o_id and s3 == -1:
                    # iterate over vehicle in current zone
                    for veh in self.zone_group[o_id][status]:
                        if not veh.valid_trans():
                            continue 
                        # get the on board passenger 
                        p2 = veh.taxi_status[2][1]
                        # get the destination of on board passenger
                        pdx, pdy = p2.dx, p2.dy             
                        # feasible zone of Case 4 inter intra (p v)
                        # determine whether the on board passenger is in the feasible region by coming passenger
                        # xlim is the x range of feasible region 
                        if (xlim[0] <= pdx and pdx <= xlim[1] and ylim[0] <= pdy and pdy <= ylim[1]):
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist4:
                                opt_veh4, dist4 = veh, dist
            opt_veh, opt_dist = min([(opt_veh0, dist0), (opt_veh2, dist2), (opt_veh4, dist4)], key=lambda k : k[1])
        if opt_veh == None:
            passenger.status = -1
            return opt_veh, opt_dist, None
        if opt_veh == opt_veh0:
            passenger.rs_status = 0
        else: passenger.rs_status = 1
        prev_status = opt_veh.status 
        status_request = opt_veh.assign(passenger)
        self.changeVehStatus(status_request)
        self.changeZoneStatus(status_request)
        return opt_veh, opt_dist, prev_status

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
    
