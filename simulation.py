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
        self.fleet_info = [] # list of [ax, ay], [sx, sy], [ix, iy]
        self.passenger_info = [] # list of [px, py]

        # dictionary storing unserved number of passenger
        self.unserved = {i:0 for i in range(self.city.n**2)}
        # 3 dimensional list storing the traveling time of passenger 
        self.traveling_ts = [[[[], []] for j in range(self.city.n**2)] for i in range(self.city.n**2)]
        # double dictionary for state number and transition rate, just like fleet.zone_group
        self.status_record = {i:{} for i in range(self.city.n**2)}
        self.idx = 0
        # four status: idle, assigned, delivering, rebalance
        self.fleet_status = []

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
                if opt_veh == None:
                    self.unserved[p.zone.id] += 1 
                self.events.dequeue()
                p_id, p = self.events.head()
            self.fleet.rebalance()
            self.move(res)
        return 

    def update_state_transition(self):
        for zone_id in self.fleet.zone_group:
            for status in self.fleet.zone_group[zone_id]:
                if status not in self.status_record[zone_id]:
                    self.status_record[zone_id][status] = [0 for i in range(self.idx)]
                self.status_record[zone_id][status].append(len(self.fleet.zone_group[zone_id][status]))
        self.idx += 1
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
        self.update_state_transition()
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
    
    # export state transition information 
    def export_state_number(self):
        workbook = xw.Workbook(f"{self.city.n}x{self.city.n}_state_number.xlsx")
        worksheet1 = workbook.add_worksheet("status number")
        worksheet1.write(0, 0, "time t (s)")
        for i in range(self.idx):
            worksheet1.write(i+1, 0, i*self.res)
        col = 1
        for zone_id in self.status_record:
            for status in self.status_record[zone_id]:
                worksheet1.write(0, col, f"({zone_id, *status}")
                row = 1
                for num in self.status_record[zone_id][status]:
                    worksheet1.write(row, col, num)
                    row += 1
                col += 1
        workbook.close()
        return 

    def export_passenger_time(self):
        for info in self.events.queue:
            p = info[1]
            if p.status != 3:
                continue
            if p.t_end < p.t_start:
                print("shit")
            self.traveling_ts[p.zone.id][p.target_zone.id][p.rs_status].append(p.t_end - p.t_start)
        workbook = xw.Workbook(f"{self.city.n}x{self.city.n}_passenger_time.xlsx")
        worksheet1 = workbook.add_worksheet("passenger time of caller")
        worksheet2 = workbook.add_worksheet("passenger time of seeker")
        worksheet3 = workbook.add_worksheet("distance of choices")
        worksheet1.write(0, 0, "zone i \ zone j")
        worksheet2.write(0, 0, "zone i \ zone j")
        for i in range(self.city.n**2):
            worksheet1.write(0, i+1, f"{i}")
            worksheet1.write(i+1, 0, f"{i}")
            worksheet2.write(0, i+1, f"{i}")
            worksheet2.write(i+1, 0, f"{i}")
        for i in range(self.city.n**2):
            for j in range(self.city.n**2):
                l0, l1 = len(self.traveling_ts[i][j][0]), len(self.traveling_ts[i][j][1])
                avg0 = "NaN" if l0 == 0 else sum(self.traveling_ts[i][j][0])/l0
                avg1 = "NaN" if l1 == 0 else sum(self.traveling_ts[i][j][1])/l1
                worksheet1.write(i+1, j+1, avg0)
                worksheet2.write(i+1, j+1, avg1)
        new_row_idx = self.city.n**2 + 2
        worksheet1.write(new_row_idx, 0, "passenger travelling time distribution")
        worksheet2.write(new_row_idx, 0, "passenger travelling time distribution")
        idx = 0
        for i in range(self.city.n**2):
            for j in range(self.city.n**2):
                worksheet1.write(new_row_idx+1, idx, f"{(i, j)}")
                worksheet2.write(new_row_idx+1, idx, f"{(i, j)}")
                for k, t in enumerate(self.traveling_ts[i][j][0]):       
                    worksheet1.write(new_row_idx+2+k, idx, t)
                for k, t in enumerate(self.traveling_ts[i][j][1]):       
                    worksheet2.write(new_row_idx+2+k, idx, t)    
                idx += 1

        for i in range(5):
            worksheet3.write(0, i, f"Case {i}")
        curr_row = 1
        dist_infos = self.events.dist_helper()
        for i in range(self.city.n**2):
            for j in range(self.city.n**2):
                dist_ij = dist_infos[(i, j)]
                for info in dist_ij:
                    worksheet3.write(curr_row, 0, f"{(i, j)}")
                    for k in range(5):
                        worksheet3.write(curr_row, k+1, info[k])
                    curr_row += 1
        workbook.close()
        return 

    
