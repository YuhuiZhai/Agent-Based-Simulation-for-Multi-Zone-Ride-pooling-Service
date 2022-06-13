from city import City
import numpy as np
from eventQueue import EventQueue
from bus_simul.fleet_bus import Busfleet
from animation import Animation
from tqdm import tqdm
class Simulation_bus:
    def __init__(self, city:City, T:float, lmd:float, fleet_size:int, simul_type=""):
        self.clock = 0
        self.T = T
        self.fleet = {}
        self.events = {}
        self.simu_type = simul_type if simul_type in ["homogeneous", "heterogeneous"] else "homogeneous" 
        if self.simu_type == "homogeneous":
            self.city = city
            self.lmd = lmd
            self.fleet_size = fleet_size 
            self.fleet[0] = Busfleet(fleet_size, city, 0)
            self.events[0] = EventQueue(city, T, lmd, 0)
        self.fleet_info = []
        self.passenger_info = []
        self.timeline = None

    def move(self, res:float):
        self.clock += res
        for key in self.fleet:
            self.fleet[key].move(res)
            self.events[key].move(res)
    
    def update(self):
        total_sx, total_sy = [], []
        total_dx, total_dy = [], []
        total_px, total_py = [], []
        for key in self.fleet:
            [sx, sy], [dx, dy] = self.fleet[key].sketch_helper()
            [px, py] = self.events[key].sketch_helper()
            total_sx += sx; total_sy += sy; total_dx += dx; total_dy += dy
            total_px += px; total_py += py
        self.fleet_info.append([[total_sx, total_sy], [total_dx, total_dy]])
        self.passenger_info.append([[total_px, total_py]])

    def Route1(self, res:float):
        stop_loc= [(1,1), (1.5,1.5), (1.5,2.5), (1,3), (2.5, 2.5), (3, 3), (2.5, 1.5), (3, 1)]
        route = [0, 1, 2, 3, 2, 4, 5, 4, 6, 7, 6, 1]
        self.city.add_stops(stop_loc)
        self.city.add_route(route)
            
        for key in self.fleet:
            self.fleet[key].addRoute(route)
        
        self.timeline = np.arange(0, self.T, res)
        for t in tqdm(self.timeline, desc="Route 1"):
            self.update()
            self.move(res)

    def make_animation(self, compression = 100, fps=15, path=""):
        print("animation plotting")
        animation = Animation(self.city, self.fleet_info, self.passenger_info)
        fleet_pattern = ({0:"stopping", 1:"driving"},
                            {0:'g', 1:'r'},
                            'o'    
                            )
        passenger_pattern = ({0:"Passenger"}, 
                                {0:'b'},
                                'v'
                            )
        animation.plot(compression, fps, fleet_pattern, passenger_pattern, path)