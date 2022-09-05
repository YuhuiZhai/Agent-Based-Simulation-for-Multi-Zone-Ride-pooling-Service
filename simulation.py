import numpy as np
from city import City
from fleet_taxi import Taxifleet
from eventQueue import EventQueue
from tqdm import tqdm
from animation import Animation
import xlsxwriter as xw

class Simulation:
    def __init__(self, city:City, T:float, lmd_matrix=None, fleet_matrix=None, rebalance_matrix=None):
        self.clock, self.city, self.T = 0, city, T
        self.lmd_m, self.fleet_m, self.rebalance_m = lmd_matrix, fleet_matrix, rebalance_matrix
        self.fleet, self.events = Taxifleet(self.fleet_m, 0, self.city, self.T, self.rebalance_m), EventQueue(T, self.lmd_m, 0, self.city)
        self.timeline = None
        self.na, self.ns, self.ni, self.ninter, self.p = [], [], [], [], []
        self.fleet_info = [] # list of [ax, ay], [sx, sy], [ix, iy]
        self.passenger_info = [] # list of [px, py]
        # double dictionary for status_record, just like fleet.zone_group
        self.status_record, self.idx = {i:{} for i in range(self.city.n**2)}, 0


    def move(self, res:float):
        self.clock += res
        self.fleet.zone_move(res)
        self.events.move(res)

    def simple_serve(self, res:float):
        self.res = res
        self.timeline = np.arange(0, self.T, res)
        for t in tqdm(self.timeline, desc="simple_serve loading"):
            self.update()
            p_id, p = self.events.head()
            while (not self.events.empty() and p.t_start < t):
                opt_veh, dist = self.fleet.serve(p)
                self.events.dequeue()
                p_id, p = self.events.head()
            self.fleet.rebalance()
            self.move(res)
        return 

    def make_animation(self, compression = 50, fps=15, name="simulation", path=""):
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
    

    def export_state_number(self):
        workbook = xw.Workbook(f"{self.city.n}x{self.city.n}_heterogenous_simulation.xlsx")
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "time t (s)")
        for i in range(self.idx):
            worksheet.write(i+1, 0, i*self.res)
        col = 1
        for zone_id in self.status_record:
            for status in self.status_record[zone_id]:
                worksheet.write(0, col, f"({zone_id, *status}")
                row = 1
                for num in self.status_record[zone_id][status]:
                    worksheet.write(row, col, num)
                    row += 1
                col += 1
        workbook.close()
        return 

    def update(self):
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

        for zone_id in self.fleet.zone_group:
            for status in self.fleet.zone_group[zone_id]:
                if status not in self.status_record[zone_id]:
                    self.status_record[zone_id][status] = [0 for i in range(self.idx)]
                self.status_record[zone_id][status].append(len(self.fleet.zone_group[zone_id][status]))
        self.idx += 1
        return 

