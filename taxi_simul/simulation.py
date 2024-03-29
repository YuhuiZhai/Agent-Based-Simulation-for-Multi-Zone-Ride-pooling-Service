import numpy as np
import math
import utils
from city import City
from taxi_simul.fleet_taxi import Taxifleet
from eventQueue import EventQueue
from tqdm import tqdm
from animation import Animation
import pandas as pd
import pulp
import scipy.optimize as sp

class Simulation:
    def __init__(self, city:City, T:float, simul_type="", lmd=None, fleet_size=None, 
                lmd_map=None, fleet_map=None, gr = True, threshold_map = None, lr  = True,
                swap=True, split=False):
        self.clock, self.T = 0, T
        self.fleet, self.events = {}, {}
        self.lr, self.gr, self.swap, self.split = lr, gr, swap, split
        self.simu_type = simul_type if simul_type in ["homogeneous", "heterogeneous"] else "homogeneous" 
        if self.simu_type == "homogeneous":
            self.city, self.lmd = city, lmd
            self.fleet_size = fleet_size if fleet_size != None else 1.5*utils.optimal(self.city, self.lmd)[4]
            self.fleet[0] = Taxifleet(fleet_size, self.city, 0)
            self.events[0] = EventQueue(self.city, T, lmd, 0)

        # rng should be adjusted for heterogeneous case in the future
        elif self.simu_type == "heterogeneous":
            self.lmd_map, self.fleet_map, self.gr, self.threshold_map = lmd_map, fleet_map, gr, threshold_map
            self.fleet_size, self.lmd = sum(sum(i) for i in fleet_map), sum(sum(i) for i in lmd_map) 
            self.city = City(city.type_name, length=city.length*len(self.lmd_map), origin=(0, 0))
            self.temp = city        
            self.hetero_init()    
        self.timeline = None
        self.na, self.ns, self.ni, self.ninter, self.p = [], [], [], [], []
        self.fleet_info = [] # list of [ax, ay], [sx, sy], [ix, iy]
        self.passenger_info = [] # list of [px, py]
        
        # testing
        self.status1, self.status2 = [], []
    
    def hetero_init(self):
        num_per_line = len(self.lmd_map)
        for i in range(num_per_line):
            for j in range(num_per_line):
                subcity = City(self.temp.type_name, length=self.temp.length, origin=(i*self.temp.length, (num_per_line-1-j)*self.temp.length), rng=self.rng)
                subfleet = Taxifleet(self.fleet_map[i][j], subcity, str(i*num_per_line+j))
                subevents = EventQueue(subcity, self.T, self.lmd_map[i][j], str(i*num_per_line+j))
                self.fleet[subfleet.id] = subfleet
                self.events[subevents.id] = subevents

    def move(self, res:float):
        self.clock += res
        for key in self.fleet:
            if self.swap:
                self.fleet[key].swap()
            self.fleet[key].move(res)
            self.events[key].move(res)

    def update(self, res:float):
        if self.simu_type == "heterogeneous" and self.gr and int(self.clock/res) % 200 == 0:
            self.global_reallocation()
        total_na, total_ns, total_ni, total_ninter = 0, 0, 0, 0
        total_ax, total_ay = [], []
        total_sx, total_sy = [], []
        total_ix, total_iy = [], []
        total_interx, total_intery = [], []
        total_px, total_py = [], []
        for key in self.fleet:
            total_na += len(self.fleet[key].vehs_group[0])
            total_ns += len(self.fleet[key].vehs_group[1])
            total_ni += len(self.fleet[key].vehs_group[2])
            total_ninter += len(self.fleet[key].vehs_group[3])
            [px, py] = self.events[key].sketch_helper()
            total_px += px; total_py += py
            [ax, ay], [sx, sy], [ix, iy], [interx, intery] = self.fleet[key].sketch_helper()
            total_ax += ax; total_ay += ay; total_sx += sx; total_sy += sy
            total_ix += ix; total_iy += iy; total_interx += interx; total_intery += intery; 
            if int(self.clock/res) % 200 == 0:
                self.fleet[key].local_reallocation(self.lr)
        self.na.append(total_na)
        self.ns.append(total_ns)
        self.ni.append(total_ni)
        self.ninter.append(total_ninter)
        self.fleet_info.append([[total_ax, total_ay], [total_sx, total_sy], [total_ix, total_iy], [total_interx, total_intery]])
        self.passenger_info.append([[total_px, total_py]])
        if self.split:
            opt_ta = self.opt_data()[0]
            if total_ni == 0 or math.sqrt(self.city.length**2/total_ni)/2/self.city.max_v > opt_ta:
                self.status2.append((self.clock, total_na, total_ns, total_ni))
            else:
                self.status1.append((self.clock, total_na, total_ns, total_ni))
        return 
    def global_reallocation(self):
        if self.simu_type == "homogeneous":
            return 
        # key is id, value is (free veh number, idx in list)
        supply_fleet, demand_fleet = {}, {}
        supply_name, demand_name = [], []
        supply_sum, demand_sum = 0, 0
        for key in self.fleet:
            subfleet, subevent = self.fleet[key], self.events[key]
            ni, lmdR = len(subfleet.vehs_group[2]), subevent.lmd 
            if self.threshold_map != None: 
                opt_ni = self.threshold_map[int(int(key)/len(self.threshold_map))][int(int(key)%len(self.threshold_map))]
            else: opt_ni = math.ceil(utils.optimal(subfleet.city, lmdR)[1])
            if (ni > opt_ni):
                supply_fleet[subfleet.id] = ni - opt_ni
                supply_name.append(subfleet.id)
                supply_sum += ni - opt_ni
            elif (ni < opt_ni):
                demand_fleet[subfleet.id] = opt_ni - ni
                demand_name.append(subfleet.id) 
                demand_sum += opt_ni - ni
        if (len(supply_fleet) == 0 or len(demand_fleet) == 0):
            return 
        supply_name.append("D")
        demand_name.append("D")
        supply_fleet["D"], demand_fleet["D"] = 0, 0 
        costs = np.zeros((len(supply_fleet), len(demand_fleet)))
        if (supply_sum < demand_sum): supply_fleet["D"] = demand_sum - supply_sum
        elif (supply_sum > demand_sum): demand_fleet["D"] = supply_sum - demand_sum
        inf = 1000  
        row_idx = 0      
        for s_id in supply_fleet:
            if s_id == "D": continue
            s = self.fleet[s_id]
            col_idx = 0
            for d_id in demand_fleet:
                if d_id == "D": continue
                d = self.fleet[d_id]
                if abs(sum(s.city.origin)/s.city.length-sum(d.city.origin)/d.city.length) != 1:
                    costs[row_idx][col_idx] = inf
                else: costs[row_idx][col_idx] = 1/demand_fleet[d_id]
                col_idx += 1
            row_idx += 1
        prob = pulp.LpProblem("transproblem", pulp.LpMinimize)
        Routes = [(s_id,d_id) for s_id in supply_name for d_id in demand_name]
        pulp_costs = pulp.makeDict([supply_name, demand_name], costs, 0)
        vars = pulp.LpVariable.dicts("Route", (supply_name, demand_name), 0, None, pulp.LpInteger)
        prob += pulp.lpSum([vars[s_id][d_id]*pulp_costs[s_id][d_id] for (s_id, d_id) in Routes])
        for s_id in supply_name:
            prob += pulp.lpSum([vars[s_id][d_id] for d_id in demand_name]) <= supply_fleet[s_id]
        for d_id in demand_name:
            prob += pulp.lpSum([vars[s_id][d_id] for s_id in supply_name]) >= demand_fleet[d_id]
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        for v in prob.variables():
            s_id, d_id = v.name.split("_")[1], v.name.split("_")[2]
            if s_id == "D" or d_id == "D" or pulp_costs[s_id][d_id] == inf:
                continue
            self.fleet[s_id].global_reallocation(self.fleet[d_id], v.varValue)
        return 

    def simple_serve(self, res:float):
        prev = 0
        self.timeline = np.arange(0, self.T, res)
        for t in tqdm(self.timeline, desc="simple_serve loading"):
            self.update(res)
            for key in self.fleet:
                p_id, p = self.events[key].head()
                while (not self.events[key].empty() and p.t_start < t):
                    prev += 1
                    self.fleet[key].simple_serve(p)
                    self.events[key].dequeue()
                    p_id, p = self.events[key].head()
            self.p.append(prev)
            self.move(res)
        return 

    # def sharing_serve(self, res:float, detour_percentage:float):
    def sharing_serve(self, res:float, detour_dist:float):
        prev = 0
        self.timeline = np.arange(0, self.T, res)
        for t in self.timeline:
        # for t in tqdm(self.timeline, desc="sharing_serve loading"):
            self.update(res)
            for key in self.fleet:
                p_id, p = self.events[key].head()
                while (not self.events[key].empty() and p.t_start < t):
                    self.fleet[key].sharing_serve(p, detour_dist)
                    prev += 1
                    self.events[key].dequeue()
                    p_id, p = self.events[key].head()
            self.move(res)
            self.p.append(prev)
        return

    def batch_serve(self, res:float, dt:float, r=math.inf):
        self.timeline = np.arange(0, self.T, res)
        batch_timeline = np.arange(0, self.T, dt)
        batch_idx = 0
        prev = 0
        # batch data vs each framing time
        batch_data = [[], [], [], [], [], [], []]
        for t in tqdm(self.timeline, desc="batch_serve loading"):
        # for t in self.timeline:
            self.update(res)
            # when it is batching time, starts serving
            if (batch_idx >= len(batch_timeline)):
                batch_time = self.timeline[-1]
            else:
                batch_time = batch_timeline[batch_idx] 
            if batch_time <= t:
                for key in self.fleet:
                    passengers = []
                    p_id, p = self.events[key].head()
                    while (not self.events[key].empty() and p.t_start < batch_time):
                        prev += 1
                        passengers.append(p)
                        self.events[key].dequeue()
                        p_id, p = self.events[key].head()
                    if len(passengers) != 0 and len(self.fleet[key].vehs_group[2]) != 0:
                        batch_data[4].append(len(self.fleet[key].vehs_group[0]))
                        batch_data[5].append(len(self.fleet[key].vehs_group[1]))
                        batch_data[6].append(len(self.fleet[key].vehs_group[2]))
                        pax_num, taxi_num = len(passengers), len(self.fleet[key].vehs_group[2])
                        unserved, pickup_dist = self.fleet[key].batch_serve(passengers, r)
                        served_num = pax_num - len(unserved)
                        avg_pickup_dist = sum(pickup_dist)/len(pickup_dist) if len(pickup_dist) != 0 else 0  
                        batch_data[0].append(served_num)
                        batch_data[1].append(pax_num)
                        batch_data[2].append(taxi_num)
                        batch_data[3].append(avg_pickup_dist)
                        # passengers not matched still stayed in the queue
                        for pax in unserved:
                            self.events[key].insert(pax)
                batch_idx += 1
            self.move(res)
            self.p.append(prev)   

        avg_m = sum(batch_data[0])/len(batch_data[0])
        avg_mpax = sum(batch_data[1])/len(batch_data[1])
        avg_mveh = sum(batch_data[2])/len(batch_data[2])
        avg_pdist = sum(batch_data[3])/len(batch_data[3])
        return batch_data, (avg_m, avg_mpax, avg_mveh, avg_pdist)
    
    def num_data(self):
        na = sum(self.na)/len(self.na)
        ns = sum(self.ns)/len(self.ns)
        ni = sum(self.ni)/len(self.ni)
        return (na, ns, ni)

    def passenger_data_share(self):
        (t1, t2, t3), (avgt1, avgt2, avgt3), (ta1, ta2, ta3), (avgta1, avgta2, avgta3) = self.events[0].sharing_info()
        return (avgt1, avgt2, avgt3), (avgta1, avgta2, avgta3) 

    def passenger_data_batch(self, combined=False, steady=False):
        if (self.simu_type == "heterogeneous"):
            return 
        (tm, ta, ts, t), (avgtm, avgta, avgts, avgt) = self.events[0].batch_info(combined, steady)
        return (tm, ta, ts, t), (avgtm, avgta, avgts, avgt)

    def fleet_data(self):
        if (self.simu_type == "heterogeneous"):
            return 
        dist_a, dist_s, ta, ts, freq, unserved = self.fleet[0].homo_info()
        tm, avg_tm = self.fleet[0].batch_info()
        avg_freq = sum(freq) / len(freq)
        avg_ta, avg_ts = sum(ta)/len(ta)/avg_freq, sum(ts)/len(ts)/avg_freq
        avg_na, avg_ns, avg_ni = sum(self.na) / len(self.na), sum(self.ns) / len(self.ns), sum(self.ni) / len(self.ni)
        return (avg_tm, avg_ta), (avg_na, avg_ns, avg_ni), ([i*self.T/len(self.na) for i in range(len(self.na))], self.na, self.ns, self.ni)
    
    def opt_data(self):
        M = self.fleet_size
        k, L, R, v, lmd = 0.5, 2**(1/2)/3*self.city.length, self.city.length**2, self.city.max_v, self.lmd
        if self.city.type_name == "Manhattan":
            k = 0.63
            L = 2/3*self.city.length
        def f(Ta):
            opt_M = k**2*R/(v*Ta)**2 + lmd*Ta + lmd*L/v - self.fleet_size
            return opt_M
        opt = (2*0.63**2*R/v**2/lmd)**(1/3)
        sol = sp.root_scalar(f, bracket=[10e-10, opt], method='bisect')
        ideal_ta = sol.root
        ideal_na, ideal_ns, ideal_ni = lmd*ideal_ta, lmd*L/v, k**2*R/(v*ideal_ta)**2  
        return (ideal_ta, ideal_na, ideal_ns, ideal_ni)

    def error(self, mesg = True):
        avg_ta, avg_ts, avg_na, avg_ns, avg_ni = self.fleet_data()
        ideal_ta, ideal_na, ideal_ns, ideal_ni = self.opt_data()
        error_ta = abs(avg_ta-ideal_ta)/ideal_ta
        error_na, error_ns, error_ni = abs(avg_na-ideal_na)/ideal_na, abs(avg_ns-ideal_ns)/ideal_ns, abs(avg_ni-ideal_ni)/ideal_ni
        if mesg:
            print("ideal ta / simulated ta / relative error: \n",  ideal_ta, "/", avg_ta, "/", error_ta*100, "%")
            print("ideal na / simulated na / relative error: \n", ideal_na, "/", avg_na, "/", error_na*100, "%")
            print("ideal ns / simulated ns / relative error: \n", ideal_ns, "/", avg_ns, "/", error_ns*100, "%")
            print("ideal ni / simulated ni / relative error: \n", ideal_ni, "/", avg_ni, "/", error_ni*100, "%")
        return error_ta, error_na, error_ns, error_ni

    def export(self, name="", path=""):
        name_ = name
        if (name_ != ""):
            name_ += "_"
        veh_num = {
            'time': self.timeline, 
            'passenger' : self.p,
            'na': self.na, 
            'ns': self.ns, 
            'ni': self.ni,
            'ninter': self.ninter
        }
        output_1 = pd.DataFrame(veh_num)
        if path == "":
            output_1.to_csv(name_ + 'veh_num_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
        else: output_1.to_csv(path + "/" + name_ + 'veh_num_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
        
        if (self.simu_type == "heterogeneous"):
            return 
        elif (self.simu_type == "homogeneous"):
            dist_a, dist_s, ta, ts, freq, unserved = self.fleet[0].homo_info()
            fleet_info = {
                'dist_a' : dist_a,
                'dist_s' : dist_s,
                'total_ta' : ta,
                'total_ts' : ts,
                'total_ti' : self.T - np.array(ta) - np.array(ts), 
                'freq' : freq
            }
            output_2 = pd.DataFrame(fleet_info)
            if path == "":
                output_2.to_csv(name_ + 'fleet_info_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
            else: output_2.to_csv(path + "/" + name_ + 'fleet_info_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
            print("unserved number: ", unserved)
        return 

    def make_animation(self, compression = 100, fps=15, name="simulation", path=""):
            print("animation plotting")
            animation = Animation(self.city, self.fleet_info, self.passenger_info)
            fleet_pattern = ({0:"assigned", 1:"in_service", 2:"idle", 3:"interchanged"},
                             {0:'y', 1:'r', 2:'g', 3:'k'},
                             'o'    
                             )
            passenger_pattern = ({0:"Passenger"}, 
                                 {0:'b'},
                                 'v'
                                )
            if name == "":
                animation.plot(compression, fps, fleet_pattern, passenger_pattern, "simulation", path)
            else: animation.plot(compression, fps, fleet_pattern, passenger_pattern, name, path)
    
