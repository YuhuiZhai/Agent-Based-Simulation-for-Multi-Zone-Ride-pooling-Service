import numpy as np
from city import City
from fleet_taxi import Taxifleet
from eventQueue import EventQueue
from tqdm import tqdm
from animation import Animation

class Simulation:
    def __init__(self, city:City, T:float, lmd_matrix=None, fleet_matrix=None):
        self.clock, self.T, self.lmd_m, self.fleet_m = 0, T, lmd_matrix, fleet_matrix
        self.city = city
        self.fleet, self.events = Taxifleet(self.fleet_m, 0, self.city), 
        
        self.timeline = None
        self.na, self.ns, self.ni, self.ninter, self.p = [], [], [], [], []
        self.fleet_info = [] # list of [ax, ay], [sx, sy], [ix, iy]
        self.passenger_info = [] # list of [px, py]
    
    def move(self, res:float):
        self.clock += res
        self.fleet.move(res)
        self.events.move(res)

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
    
    def update(self, res:float):
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
        return 