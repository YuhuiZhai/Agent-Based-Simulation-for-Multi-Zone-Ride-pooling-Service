import numpy as np
import utils
from city import City
from fleet import Fleet
from eventQueue import EventQueue
from tqdm import tqdm
import pandas as pd
from animation import Animation
class Simulation:
    def __init__(self, city:City, T:float, lmd:float, fleet_size=None, simul_type="", lmd_map=None, fleet_map=None, realloc_decision  = True):
        self.clock = 0
        self.T = T
        self.lmd = lmd
        self.fleet = []
        self.events = []
        self.realloc_decision = realloc_decision 
        self.simu_type = simul_type if simul_type in ["homogeneous", "heterogeneous"] else "homogeneous" 
        if self.simu_type == "homogeneous":
            self.city = city
            self.fleet_size = fleet_size if fleet_size != None else 1.5*utils.optimal(self.city, self.lmd)[4]
            self.fleet.append(Fleet(fleet_size, city))
            self.events.append(EventQueue(city, T, lmd))
        elif self.simu_type == "heterogeneous":
            self.lmd_map = lmd_map
            self.fleet_map = fleet_map
            self.city = City(city.type_name, length=city.length*len(self.lmd_map), origin=(0, 0))
            self.temp = city        
            self.hetero_init()    
      
        # na, ns, ni, p vs t
        self.timeline = None
        self.na, self.ns, self.ni, self.p = [], [], [], []
        # list of [ax, ay], [sx, sy], [ix, iy]
        self.fleet_info = []
        # list of [px, py]
        self.passenger_info = []
    
    def hetero_init(self):
        num_per_line = len(self.lmd_map)
        for i in range(num_per_line):
            for j in range(num_per_line):
                subcity = City(self.temp.type_name, length=self.temp.length, origin=(i*self.temp.length, (num_per_line-1-j)*self.temp.length))
                subfleet = Fleet(self.fleet_map[i][j], subcity)
                subevents = EventQueue(subcity, self.T, self.lmd_map[i][j])
                self.fleet.append(subfleet)
                self.events.append(subevents)

    def move(self, res:float):
        self.clock += res
        for i in range(len(self.fleet)):
            self.fleet[i].move(res)
            self.events[i].move(res)

    def update(self, res):
        if int(self.clock/res) % 30 == 0:
            self.global_reallocation()
        total_na, total_ns, total_ni = 0, 0, 0
        total_ax, total_ay = [], []
        total_sx, total_sy = [], []
        total_ix, total_iy = [], []
        total_interx, total_intery = [], []
        total_px, total_py = [], []
        for i in range(len(self.fleet)):
            total_na += self.fleet[i].assigned_num 
            total_ns += self.fleet[i].inservice_num
            total_ni += self.fleet[i].idle_num
            [ax, ay], [sx, sy], [ix, iy], [interx, intery] = self.fleet[i].sketch_helper()
            [px, py] = self.events[i].sketch_helper()
            total_ax += ax; total_ay += ay; total_sx += sx; total_sy += sy
            total_ix += ix; total_iy += iy; total_interx += interx; total_intery += intery; 
            total_px += px; total_py += py
            self.fleet[i].local_reallocation(self.realloc_decision)
        self.na.append(total_na)
        self.ns.append(total_ns)
        self.ni.append(total_ni)
        self.fleet_info.append([[total_ax, total_ay], [total_sx, total_sy], [total_ix, total_iy], [total_interx, total_intery]])
        self.passenger_info.append([total_px, total_py])
        
    def reset(self):
        self.timeline = None
        self.na, self.ns, self.ni, self.p = [], [], [], []
        self.fleet_info, self.passenger_info = [], []
        if self.simu_type == "homogeneous":
            self.fleet = [Fleet(self.fleet_size, self.city)]
            self.events = [EventQueue(self.city, self.T, self.lmd)]
        elif self.simu_type == "heterogeneous":
            self.hetero_init()

    def global_reallocation(self):
        free_fleet = {}
        hard_fleet = {}
        if self.simu_type == "homogeneous":
            return 
        for i in range(len(self.fleet)):
            subfleet = self.fleet[i]
            subevent = self.events[i]
            ni = subfleet.idle_num
            lmdR = subevent.lmd
            opt_ni = utils.optimal(subfleet.city, lmdR)[1]    
            if (ni > opt_ni):
                free_fleet[subfleet] = ni - opt_ni
            else:
                hard_fleet[subfleet] = ni - opt_ni 
        for ff in free_fleet:
            for hf in hard_fleet:
                ff.global_reallocation(hf, int(0.3*free_fleet[ff]/len(hard_fleet)))

    def simple_serve(self, res:float):
        prev = 0
        self.timeline = np.arange(0, self.T, res)
        for t in tqdm(self.timeline, desc="simple_serve loading"):
            self.update(res)
            for i in range(len(self.fleet)):
                head_time, head = self.events[i].head()
                while (not self.events[i].empty() and head_time < t):
                    prev += 1
                    self.fleet[i].simple_serve(head.passenger)
                    self.events[i].dequeue()
                    head_time, head = self.events[i].head()
            self.p.append(prev)
            self.move(res)
        return 

    def sharing_serve(self, res:float, detour_percentage:float):
        prev = 0
        self.timeline = np.arange(0, self.T, res)
        for t in tqdm(self.timeline, desc="sharing_serve loading"):
            for i in range(len(self.fleet)):
                self.update(res)
                for i in range(len(self.fleet)):
                    head_time, head = self.events[i].head()
                    while (not self.events[i].empty() and head_time < t):
                        self.fleet[i].sharing_serve(head.passenger, detour_percentage)
                        prev += 1
                        self.events[i].dequeue()
                        head_time, head = self.events[i].head()
            self.move(res)
            self.p.append(prev)
        return

    def batch_serve(self, res:float, dt:float):
        self.timeline = np.arange(0, self.T, res)
        batch_timeline = np.arange(0, self.T, dt)
        batch_idx = 0
        prev = 0
        
        for t in tqdm(self.timeline, desc="batch_serve loading"):
            self.update(res)
            # when it is batching time, starts serving
            if (batch_idx >= len(batch_timeline)):
                batch_time = self.timeline[-1]
            else:
                batch_time = batch_timeline[batch_idx] 
            if batch_time <= t:
                for i in range(len(self.fleet)):
                    passengers = []
                    head_time, head = self.events[i].head()
                    while (not self.events[i].empty() and head_time < batch_time):
                        prev += 1
                        passengers.append(head.passenger)
                        self.events[i].dequeue()
                        head_time, head = self.events[i].head()
                    if len(passengers) != 0:
                        self.fleet[i].batch_serve(passengers)
                    batch_idx += 1
            self.move(res)
            self.p.append(prev)     
        return   

    # def sharing_serve(self, res:float, detour_dist=0, detour_percent=0):
    def export(self, name=""):
        name_ = name
        if (name_ != ""):
            name_ += "_"
        veh_num = {
            'time': self.timeline, 
            'passenger' : self.p,
            'na': self.na, 
            'ns': self.ns, 
            'ni': self.ni 
        }
        output_1 = pd.DataFrame(veh_num)
        output_1.to_csv(name_ + 'veh_num_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
        if (self.simu_type == "heterogeneous"):
            return 
        elif (self.simu_type == "homogeneous"):
            dist_a, dist_s, ta, ts, freq, unserved = self.fleet[0].info()
            fleet_info = {
                'dist_a' : dist_a,
                'dist_s' : dist_s,
                'total_ta' : ta,
                'total_ts' : ts,
                'total_ti' : self.T - np.array(ta) - np.array(ts), 
                'freq' : freq
            }
            output_2 = pd.DataFrame(fleet_info)
            output_2.to_csv(name_ + 'fleet_info_M_' + str(self.fleet_size) + '_lambda_' + str(self.lmd) + '.csv')
            print("unserved number: ", unserved)
        return 

    def make_animation(self, compression = 100, fps=15):
            print("animation plotting")
            animation = Animation(self.city, self.fleet_info, self.passenger_info)
            animation.plot(compression, fps)
    
