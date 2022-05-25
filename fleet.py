from sympy import true
from vehicle import Vehicle
import matplotlib.pyplot as plt
import math 
import numpy as np
import utils 
from tqdm import tqdm 
from city import City
from passenger import Passenger
from scipy.optimize import linear_sum_assignment

class Fleet:
    def __init__(self, n:int, city:City):
        self.clock = 0
        self.fleet_size = n
        self.vehicles = {}
        self.city = city
        self.assigned_num = 0
        self.inservice_num = 0
        self.idle_num = n
        self.unserved_num = 0
        for i in range(n):
            self.vehicles[i] = Vehicle(i, city)

    # dist_type is [1: assigned distance, 2: service distance, 3:total distance]
    def dist(self, vehicle:Vehicle, passenger:Passenger, dist_type:int):
        i_table = {1:[1, 0], 2:[0, 1], 3:[1, 1]} 
        i1, i2 = i_table[dist_type]

        if self.city.type_name == "Euclidean":
            dist = i1*((vehicle.x-passenger.ox)**2 + (vehicle.y-passenger.oy)**2)**(0.5) \
                + i2*((passenger.ox-passenger.dx)**2 + (passenger.oy-passenger.dy)**2)**(0.5)
            return dist

        if self.city.type_name == "Manhattan":
            dist = i1*(abs(vehicle.x - passenger.ox) + abs(vehicle.y - passenger.oy)) \
                +  i2*(abs(passenger.ox - passenger.dx) + abs(passenger.oy - passenger.dy))
            return dist

        if self.city.type_name == "real-world":
            v_link, v_len = vehicle.link, vehicle.len
            o_link, o_len = passenger.o_link, passenger.o_len
            d_link, d_len = passenger.d_link, passenger.d_len
            dist1, path1 = self.city.dijkstra(v_link.origin.id, o_link.origin.id)
            dist2, path2 = self.city.dijkstra(o_link.origin.id, d_link.origin.id)
            if dist1 == -1 or dist2 == -1:
                return -1
            if (len(path1) == 1):
                if (v_link.id == o_link.id):
                    dist = i1*v_len + i2*(dist2 + d_len)
                else:
                    dist = i1*abs(v_len-o_len) + i2*(dist2 - o_len + d_len)
            if (len(path1) > 1):
                if (v_link.id == self.city.map[path1[0], path1[1]]):
                    dist = i1*(dist1 - v_len) + i2*(dist2 - d_len)
                else:
                    dist = i1*(dist1 + v_len) + i2*(dist2 + d_len) 
            return dist
    
    def detour_dist(self, O:tuple, D:tuple, P:tuple):
            ox, oy = O
            dx, dy = D
            px, py = P
            return 2*(max(ox-px, 0) + max(oy-py, 0) + max(px-dx, 0) + max(py-dy, 0))
    
    # find optimal match of idle vehicle and passenger based on distance
    def best_match_i(self, passenger:Passenger):
        min_dist = math.inf
        opt_veh = None
        for id in self.vehicles:
            vehicle = self.vehicles[id]
            if vehicle.status == "idle":
                temp_dist = self.dist(vehicle, passenger, 3)
                if temp_dist < 0:
                    continue
                if temp_dist < min_dist:
                    min_dist = temp_dist
                    opt_veh = vehicle
        return min_dist, opt_veh

    # find optimal match of service vehicle and passenger based on distance
    def best_match_s(self, passenger:Passenger, detour_percent:float):
        min_dist = math.inf
        opt_veh = None
        A, B = passenger.location()
        for id in self.vehicles:
            vehicle = self.vehicles[id]
            if vehicle.status == "in_service" and vehicle.load <= 1:
                O = vehicle.location()
                D = vehicle.passenger[0].location()[1]
                # origin detour
                dist_o = self.detour_dist(O, D, A)
                # destination detour 
                dist_d = self.detour_dist(A, D, B)
                if dist_d + dist_o <= detour_percent * self.dist(vehicle, vehicle.passenger[0], 2):
                    if (dist_d + dist_o) < min_dist:
                        min_dist = dist_d + dist_o
                        opt_veh = vehicle
        return min_dist, opt_veh


    # figure out the optimal taxi to serve the passenger 
    def simple_serve(self, passenger:Passenger):
        min_dist, opt_veh = self.best_match_i(passenger)
        if opt_veh is None:
            passenger.status = "unserved"
            self.unserved_num += 1
        else:
            opt_veh.assign(passenger)
        return

    # sharing serve based on the detour distance
    def sharing_serve(self, passenger:Passenger, detour_percent:float):
        min_dist_i, opt_veh_i = self.best_match_i(passenger)
        min_dist_s, opt_veh_s = self.best_match_s(passenger, detour_percent)
        if (opt_veh_i == None and opt_veh_s == None):
            passenger.status = "unserved"
            self.unserved_num += 1
        elif (opt_veh_i == None):
            opt_veh_s.add(passenger)
        elif (opt_veh_s == None):
            opt_veh_i.assign(passenger)
        else:
            if (min_dist_s <= min_dist_i):
                opt_veh_s.add(passenger)
            else:
                opt_veh_i.assign(passenger)
        return

    # batching assignment to serve a group of passenger 
    def batch_serve(self, passengers:list):
        # define inf as 4000 mile, which is the radius of earth (scipy.optimize has bug with inf)
        inf = 4000
        # bi direction map between nparray idx and veh
        valid_vehs = {}
        idx1 = 0
        for veh_id in self.vehicles:
            veh = self.vehicles[veh_id]
            if veh.status == "idle":
                valid_vehs[idx1] = veh
                valid_vehs[veh] = idx1
                idx1 += 1
        # initialize a objective matrix
        weight_table = inf * np.ones((len(passengers), int(len(valid_vehs)/2)))
        # bi direction map between nparray idx and pax
        valid_paxs = {}
        for idx2, pax in enumerate(passengers):
            for veh_id in self.vehicles:
                veh = self.vehicles[veh_id]
                if veh.status != "idle":
                    continue
                dist = self.dist(veh, pax, 3)
                # if there is no connecting path, the weight is still inf
                if dist == -1:
                    continue
                weight_table[idx2, valid_vehs[veh]] = dist          
            valid_paxs[idx2] = pax
            valid_paxs[pax] = idx2
        row, col = linear_sum_assignment(weight_table)
        served_num = 0
        decision_table = np.zeros(len(passengers))
        for i in range(len(row)):
            row_idx = row[i]
            col_idx = col[i]
            opt_pax = valid_paxs[row_idx]
            opt_veh = valid_vehs[col_idx]
            if (weight_table[row_idx, col_idx] == inf):
                continue
            opt_veh.assign(opt_pax)
            served_num += 1
            decision_table[valid_paxs[opt_pax]] = 1
        for i, pax in enumerate(passengers):
            if not decision_table[i]:
                pax.status = "unserved"
        self.unserved_num += len(passengers) - served_num
        return
      
    def sketch_helper(self):
        ax, ay = [], []
        sx, sy = [], []
        ix, iy = [], []
        for v_id in self.vehicles:
            v = self.vehicles[v_id]
            if (v.status == 'assigned'):
                ax.append(v.location()[0])
                ay.append(v.location()[1])
            if (v.status == 'in_service'):
                sx.append(v.location()[0])
                sy.append(v.location()[1])
            if (v.status == 'idle'):
                ix.append(v.location()[0])
                iy.append(v.location()[1])
        return [ax, ay], [sx, sy], [ix, iy]

    # function to return total driving distance, assigned time, inservice time
    def info(self):
        dist_a = []
        dist_s = []
        ta = []
        ts = []
        freq = []
        for v_idx in self.vehicles:
            veh = self.vehicles[v_idx]
            dist_a.append(veh.dist_a)
            dist_s.append(veh.dist_s)
            ta.append(veh.ta)
            ts.append(veh.ts)
            freq.append(veh.freq)
        return dist_a, dist_s, ta, ts, freq, self.unserved_num

    # function to serve the passenger at time t
    def move(self, dt):
        count1 = 0
        count2 = 0
        count3 = 0
        for id in self.vehicles:
            self.vehicles[id].move(dt)
            if self.vehicles[id].status == 'assigned':
                count1 += 1
            
            if self.vehicles[id].status == 'in_service':
                count2 += 1
            
            if self.vehicles[id].status == 'idle':
                count3 += 1
        self.clock += dt
        self.assigned_num = count1
        self.inservice_num = count2
        self.idle_num = count3