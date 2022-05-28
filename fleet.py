import utils
from vehicle import Vehicle
import math 
import numpy as np
from tqdm import tqdm 
from city import City
from passenger import Passenger
from scipy.optimize import linear_sum_assignment

class Fleet:
    def __init__(self, n:int, city:City):
        self.fleet_size, self.city = n, city
        self.id = city.origin
        self.clock = 0
        self.vehicles = {}
        self.assigned_vehs, self.in_service_vehs, self.idle_vehs = set(), set(), set()
        self.vehs_group = [self.assigned_vehs, self.in_service_vehs, self.idle_vehs]
        self.assigned_num, self.inservice_num, self.idle_num = 0, 0, n 
        self.unserved_num, self.served_num = 0, 0
        for i in range(n):
            veh = Vehicle((self.city.origin, i), city)
            self.vehicles[(self.city.origin, i)] = veh
            self.idle_vehs.add(veh)
    
    # change veh's status from status1 to status2 
    def changeVehStatus(self, status_request:tuple):
        veh_id, status1, status2 = status_request
        if status1 == status2:
            return
        veh = self.vehicles[veh_id]
        set_out, set_in = self.vehs_group[status1], self.vehs_group[status2]
        set_out.remove(veh)
        set_in.add(veh)
        return 

    # add idle vehicle from other fleet
    def add_idle(self, vehicle:Vehicle):
        self.vehicles[vehicle.id] = vehicle
        self.idle_vehs.add(vehicle)
        self.fleet_size += 1
        return 

    # release idle vehicle to other fleet
    def release_idle(self, vehicle:Vehicle):
        self.vehicles.pop(vehicle.id)
        self.idle_vehs.remove(vehicle)
        self.fleet_size -= 1
        return 

    def global_reallocation(self, fleet, num):
        sent_vehs = set()
        for idle_veh in self.idle_vehs:
            if len(sent_vehs) == num:
                break
            sent_vehs.add(idle_veh)

        for sent_veh in sent_vehs:
            sent_veh.changeCity(fleet.city)
            self.release_idle(sent_veh)
            fleet.add_idle(sent_veh)

    def local_reallocation(self, decision=True):
        if (self.city.type_name == "real-world"):
            return
        if not decision:
            for idle_veh in self.idle_vehs:
                idle_veh.idle_postion = utils.generate_location()
            return 
        valid_vehs = {}
        idx1 = 0
        for idle_veh in self.idle_vehs:
            valid_vehs[idx1] = idle_veh
            valid_vehs[idle_veh] = idx1
            idx1 += 1
        if idx1 <= 1:
            return 
        idle_pos = []
        num = int((idx1)**(0.5))
        if (num**2 != idx1):
            num += 1    
        even_space = self.city.length / (num-1)
        for i in range(int(num**2)):
            idle_pos.append((self.city.origin[0] + even_space*(i%num), self.city.origin[1] + even_space*int(i/num)))
        weight_table = np.ones((int(len(valid_vehs)/2), len(idle_pos)))
        for i in range(idx1):
            veh = valid_vehs[i]
            for j in range(len(idle_pos)):
                x, y = idle_pos[j]
                if (self.city.type_name == "Manhattan"):
                    weight_table[i, j] = abs(veh.x - x) + abs(veh.y - y)
                elif (self.city.type_name == "Euclidean"):
                    weight_table[i, j] = ((veh.x - x)**2 + (veh.y - y)**2)**(0.5)
        row, col = linear_sum_assignment(weight_table)
        for i in range(len(row)):
            row_idx, col_idx = row[i], col[i]
            opt_veh = valid_vehs[row_idx]
            opt_veh.idle_position = idle_pos[col_idx]
        return

    # dist_type is [1: assigned distance, 2: service distance, 3:total distance]
    def dist(self, vehicle:Vehicle, passenger:Passenger, dist_type:int):
        i_table = {1:[1, 0], 2:[0, 1], 3:[1, 1]} 
        i1, i2 = i_table[dist_type]

        if self.city.type_name == "Euclidean":
            dist = i1*((vehicle.x-passenger.ox)**2 + (vehicle.y-passenger.oy)**2)**(0.5) \
                + i2*((passenger.ox-passenger.dx)**2 + (passenger.oy-passenger.dy)**2)**(0.5)
            return dist

        elif self.city.type_name == "Manhattan":
            dist = i1*(abs(vehicle.x - passenger.ox) + abs(vehicle.y - passenger.oy)) \
                +  i2*(abs(passenger.ox - passenger.dx) + abs(passenger.oy - passenger.dy))
            return dist

        elif self.city.type_name == "real-world":
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
            elif (len(path1) > 1):
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
        for idle_veh in self.idle_vehs:
            temp_dist = self.dist(idle_veh, passenger, 3)
            if temp_dist < 0:
                continue
            if temp_dist < min_dist:
                min_dist = temp_dist
                opt_veh = idle_veh
        return min_dist, opt_veh

    # find optimal match of service vehicle and passenger based on distance
    def best_match_s(self, passenger:Passenger, detour_percent:float):
        min_dist = math.inf
        opt_veh = None
        A, B = passenger.location()
        for in_service_veh in self.in_service_vehs:
            if in_service_veh.load > 1:
                continue
            O = in_service_veh.location()
            D = in_service_veh.passenger[0].location()[1]
            # origin detour
            dist_o = self.detour_dist(O, D, A)
            # destination detour 
            dist_d = self.detour_dist(A, D, B)
            if dist_d + dist_o <= detour_percent * self.dist(in_service_veh, in_service_veh.passenger[0], 2):
                if (dist_d + dist_o) < min_dist:
                    min_dist = dist_d + dist_o
                    opt_veh = in_service_veh
        return min_dist, opt_veh


    # figure out the optimal taxi to serve the passenger 
    def simple_serve(self, passenger:Passenger):
        min_dist, opt_veh = self.best_match_i(passenger)
        if opt_veh is None:
            passenger.status = "unserved"
            self.unserved_num += 1
            return False   
        status_request = opt_veh.assign(passenger)
        self.changeVehStatus(status_request)
        self.served_num += 1
        return True

    # sharing serve based on the detour distance
    def sharing_serve(self, passenger:Passenger, detour_percent:float):
        min_dist_i, opt_veh_i = self.best_match_i(passenger)
        min_dist_s, opt_veh_s = self.best_match_s(passenger, detour_percent)
        if (opt_veh_i == None and opt_veh_s == None):
            passenger.status = "unserved"
            self.unserved_num += 1
            return False
        elif (opt_veh_i == None):
            opt_veh_s.add(passenger)
        elif (opt_veh_s == None):
            status_request = opt_veh_i.assign(passenger)
            self.changeVehStatus(status_request)
        else:
            if (min_dist_s <= min_dist_i):
                opt_veh_s.add(passenger)
            else:
                status_request = opt_veh_i.assign(passenger)
                self.changeVehStatus(status_request)
        self.served_num += 1
        return True

    # batching assignment to serve a group of passenger 
    def batch_serve(self, passengers:list):
        inf = 4000
        # bi direction map between nparray idx and veh
        valid_vehs = {}
        idx1 = 0
        for idle_veh in self.idle_vehs:
            valid_vehs[idx1], valid_vehs[idle_veh] = idle_veh, idx1
            idx1 += 1
        weight_table = inf * np.ones((len(passengers), int(len(valid_vehs)/2)))
        # bi direction map between nparray idx and pax
        valid_paxs = {}
        for idx2, pax in enumerate(passengers):
            for idle_veh in self.idle_vehs:
                dist = self.dist(idle_veh, pax, 3)
                # if there is no connecting path, the weight is still inf
                if dist == -1:
                    continue
                weight_table[idx2, valid_vehs[idle_veh]] = dist          
            valid_paxs[idx2], valid_paxs[pax] = pax, idx2
        row, col = linear_sum_assignment(weight_table)
        served_num = 0
        decision_table = np.zeros(len(passengers))
        for i in range(len(row)):
            row_idx, col_idx = row[i], col[i]
            opt_pax, opt_veh = valid_paxs[row_idx], valid_vehs[col_idx]
            if (weight_table[row_idx, col_idx] == inf):
                continue
            status_request = opt_veh.assign(opt_pax)
            self.changeVehStatus(status_request)
            served_num += 1
            decision_table[valid_paxs[opt_pax]] = 1
        for i, pax in enumerate(passengers):
            if not decision_table[i]:
                pax.status = "unserved"
        self.unserved_num += len(passengers) - served_num
        self.served_num += served_num
        return
      
    def sketch_helper(self):
        ax, ay = [], []
        sx, sy = [], []
        ix, iy = [], []
        for veh_a in self.assigned_vehs:
            ax.append(veh_a.location()[0])
            ay.append(veh_a.location()[1])
        for veh_s in self.in_service_vehs:
            sx.append(veh_s.location()[0])
            sy.append(veh_s.location()[1])
        for veh_i in self.idle_vehs:
            ix.append(veh_i.location()[0])
            iy.append(veh_i.location()[1])
        return [ax, ay], [sx, sy], [ix, iy]

    # function to return total driving distance, assigned time, inservice time
    def info(self):
        dist_a, dist_s = [], []
        ta, ts = [], []
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
        for id in self.vehicles:
            status_request = self.vehicles[id].move(dt)
            self.changeVehStatus(status_request)
        self.clock += dt
        self.assigned_num = len(self.assigned_vehs)
        self.inservice_num = len(self.in_service_vehs) 
        self.idle_num = len(self.idle_vehs)

    def approx_lmdR(self):
        return self.served_num/self.clock
    
