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

    def dist(self, vehicle:Vehicle, passenger:Passenger):
        if self.city.type_name == "Euclidean":
            dist = ((vehicle.x-passenger.ox)**2 + (vehicle.y-passenger.oy)**2)**(0.5) \
                + ((passenger.ox-passenger.dx)**2 + (passenger.oy-passenger.dy)**2)**(0.5)
            return dist

        if self.city.type_name == "Manhattan":
            dist = abs(vehicle.x - passenger.ox) + abs(vehicle.y - passenger.oy) \
                +  abs(passenger.ox - passenger.dx) + abs(passenger.oy - passenger.dy)
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
                    dist = dist2 + v_len + d_len
                else:
                    dist = dist2 + v_len + 2*d_len
            if (len(path1) > 1):
                if (v_link.id == self.city.map[path1[0], path1[1]]):
                    dist = dist1 + dist2 - v_len
                else:
                    dist = dist1 + dist2 + v_len

                dist = dist1 + dist2 - o_len + d_len  
            return dist

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

    # figure out the optimal taxi to serve the passenger 
    def simple_serve(self, passenger:Passenger):
        min_dist = math.inf
        opt_veh = None
        for id in self.vehicles:
            vehicle = self.vehicles[id]
            if vehicle.status == "idle":
                temp_dist = self.dist(vehicle, passenger)
                if temp_dist <= 0:
                    continue
                if temp_dist < min_dist:
                    min_dist = temp_dist
                    opt_veh = vehicle
        if opt_veh is None:
            self.unserved_num += 1
            return False
        else:
            opt_veh.assign(passenger)
            return True

    # batching assignment to serve a group of passenger 
    def batch_serve(self, passengers:list):
        # define inf as 4000 mile, which is the radius of earth (scipy.optimize has bug with inf)
        inf = 4000
        # bi direction map between nparray idx and veh
        valid_vehs = {}
        temp1 = 0
        for veh_id in self.vehicles:
            veh = self.vehicles[veh_id]
            if veh.status == "idle":
                valid_vehs[temp1] = veh
                valid_vehs[veh] = temp1
                temp1 += 1

        # initialize a objective matrix
        obj_table = 4000 * np.ones((len(passengers), int(len(valid_vehs)/2)))

        # bi direction map between nparray idx and pax
        valid_paxs = {}
        temp2 = 0
        for pax in passengers:
            for veh_id in self.vehicles:
                veh = self.vehicles[veh_id]
                if veh.status != "idle":
                    continue
                dist = self.dist(veh, pax)
                # if there is no connecting path, the weight is still inf
                if dist == -1:
                    continue
                obj_table[temp2, valid_vehs[veh]] = dist          
            valid_paxs[temp2] = pax
            valid_paxs[pax] = temp2
            temp2 += 1
        row, col = linear_sum_assignment(obj_table)
        served_num = 0
        for i in range(len(row)):
            row_idx = row[i]
            col_idx = col[i]
            opt_pax = valid_paxs[row_idx]
            opt_veh = valid_vehs[col_idx]
            if (obj_table[row_idx, col_idx] == 4000):
                continue
            opt_veh.assign(opt_pax)
            served_num += 1
        self.unserved_num += len(passengers) - served_num
        return


    # return the 
    def sketch_helper(self):
        ax, ay = [], []
        sx, sy = [], []
        ix, iy = [], []
        px, py = [], []
        count = 0
        for v_id in self.vehicles:
            if (count >= 10):
                break
            count += 1
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
            if (v.passenger is not None and v.passenger.status == 'not picked up'):
                px.append(v.passenger.location()[0])
                py.append(v.passenger.location()[1])
        return [ax, ay], [sx, sy], [ix, iy], [px, py]