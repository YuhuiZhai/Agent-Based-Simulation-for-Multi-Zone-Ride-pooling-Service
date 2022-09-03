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
        self.fleet, self.events = Taxifleet(self.fleet_m, 0, self.city), EventQueue(T, self.lmd_m, 0, self.city)
        self.timeline = None
        self.na, self.ns, self.ni, self.ninter, self.p = [], [], [], [], []
        self.fleet_info = [] # list of [ax, ay], [sx, sy], [ix, iy]
        self.passenger_info = [] # list of [px, py]
    
    def move(self, res:float):
        self.clock += res
        self.fleet.zone_move(res)
        self.events.move(res)

    def simple_serve(self, res:float):
        self.timeline = np.arange(0, self.T, res)
        for t in tqdm(self.timeline, desc="simple_serve loading"):
            self.update(res)
            p_id, p = self.events.head()
            while (not self.events.empty() and p.t_start < t):
                opt_veh, dist = self.fleet.serve(p)
                self.events.dequeue()
                p_id, p = self.events.head()
            self.move(res)
        return 

    def make_animation(self, compression = 100, fps=15, name="simulation", path=""):
            print("animation plotting")
            animation = Animation(self.city, self.fleet_info, self.passenger_info)
            fleet_pattern = ({0:"idle", 1:"assigned", 2:"in service", 3:"interchanged"},
                             {0:'g', 1:'y', 2:'r', 3:'k'},
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
        ax, ay = [], []
        sx, sy = [], []
        ix, iy = [], []
        interx, intery = [], []
        px, py = [], []

        [px, py] = self.events.sketch_helper()
        px += px; py += py
        [ax, ay], [sx, sy], [ix, iy], [interx, intery] = self.fleet.sketch_helper()
        ax += ax; ay += ay; sx += sx; sy += sy
        ix += ix; iy += iy; interx += interx; intery += intery; 
        self.fleet_info.append([[ax, ay], [sx, sy], [ix, iy], [interx, intery]])
        self.passenger_info.append([[px, py]])
        return 

