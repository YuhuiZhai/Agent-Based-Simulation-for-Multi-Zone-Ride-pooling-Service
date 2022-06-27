from fleet import Fleet
from city import City
from taxi_simul.taxi import Taxi
import utils
from scipy.optimize import linear_sum_assignment
from passenger import Passenger
import math
import numpy as np

class Taxifleet(Fleet):
    def __init__(self, n:int, city:City, id):
        super().__init__(n, city, id)
        self.init_group(
            status_name={0:"assigned", 1:"in service", 2:"idle", 3:"inter"}
        )
        self.unserved_num, self.served_num = 0, 0
        for i in range(n):
            veh = Taxi((self.id, i), city, 2)
            self.vehicles[(self.id, i)] = veh
            self.vehs_group[2].add(veh)

    def global_reallocation(self, fleet:Fleet, num:int):
        sent_vehs = set()
        for idle_veh in self.vehs_group[2]:
            if len(sent_vehs) == num:
                break
            sent_vehs.add(idle_veh)
        for sent_veh in sent_vehs:
            self.release_veh(sent_veh)
            fleet.add_veh(sent_veh)
            sent_veh.changeCity(fleet.city)
            sent_veh.idle_position = utils.generate_location(fleet.city)
            status_request = sent_veh.interchanging()
            fleet.changeVehStatus(status_request)
    
    def swap(self):
        inf = 4000
        assigned_vehs = [a for a in self.vehs_group[0]]
        idle_vehs = [i for i in self.vehs_group[2]]
        
        weight_table = inf * np.ones((len(assigned_vehs), len(idle_vehs)))
        for i, a_veh in enumerate(assigned_vehs):
            a_pax = a_veh.passenger[0]
            dist1 = self.dist(a_veh, a_pax, 1)
            for j, i_veh in enumerate(idle_vehs):
                dist2 = self.dist(i_veh, a_pax, 1)
                if  dist2 >= dist1:
                    continue
                weight_table[i, j] = dist2
        row, col = linear_sum_assignment(weight_table)
        for i in range(len(row)):
            row_idx, col_idx = row[i], col[i]
            if weight_table[row_idx, col_idx] == inf:
                continue
            av, iv = assigned_vehs[row_idx], idle_vehs[col_idx]
            (r1, r2) = av.swap(iv) 
            self.changeVehStatus(r1)
            self.changeVehStatus(r2)
        return 


    def local_reallocation(self, decision=True):
        if (self.city.type_name == "real-world"):
            return
        if not decision:
            for idle_veh in self.vehs_group[2]:
                idle_veh.idle_postion = utils.generate_location(self.city)
            return 
        valid_vehs = {}
        idx1 = 0
        for idle_veh in self.vehs_group[2]:
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
    def dist(self, vehicle:Taxi, passenger:Passenger, dist_type:int):
        i_table = {1:[1, 0], 2:[0, 1], 3:[1, 1]} 
        i1, i2 = i_table[dist_type]

        if self.city.type_name == "Euclidean":
            dist = i1*((vehicle.x-passenger.x)**2 + (vehicle.y-passenger.y)**2)**(0.5) \
                + i2*((passenger.x-passenger.dx)**2 + (passenger.y-passenger.dy)**2)**(0.5)
            return dist

        elif self.city.type_name == "Manhattan":
            dist = i1*(abs(vehicle.x - passenger.x) + abs(vehicle.y - passenger.y)) \
                +  i2*(abs(passenger.x - passenger.dx) + abs(passenger.y - passenger.dy))
            return dist

        elif self.city.type_name == "real-world":
            v_link, v_len = vehicle.link, vehicle.len
            o_link, o_len = passenger.link, passenger.len
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
        for idle_veh in self.vehs_group[2]:
            temp_dist = self.dist(idle_veh, passenger, 3)
            if temp_dist < 0:
                continue
            if temp_dist < min_dist:
                min_dist = temp_dist
                opt_veh = idle_veh
        return min_dist, opt_veh

    # find optimal match of service vehicle and passenger based on distance
    # def best_match_s(self, passenger:Passenger, detour_percent:float):
    def best_match_s(self, passenger:Passenger, detour_dist:float):
        min_dist = math.inf
        opt_veh = None
        A, B = passenger.location()
        for in_service_veh in self.vehs_group[1]:
            if in_service_veh.load > 1:
                continue
            O = in_service_veh.location()
            D = in_service_veh.passenger[0].location()[1]
            # origin detour
            dist_o = self.detour_dist(O, D, A)
            # destination detour 
            dist_d = self.detour_dist(A, D, B)
            # if (dist_d + dist_o) <= detour_percent/100 * self.dist(in_service_veh, in_service_veh.passenger[0], 2):
            if (dist_d + dist_o) <= detour_dist:
                if (dist_d + dist_o) < min_dist:

                    # possible bug
                    min_dist = dist_d + dist_o
                    
                    opt_veh = in_service_veh
        return min_dist, opt_veh

    # figure out the optimal taxi to serve the passenger 
    def simple_serve(self, passenger:Passenger):
        min_dist, opt_veh = self.best_match_i(passenger)
        if opt_veh is None:
            passenger.status = -1
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
            passenger.status = -1 
            self.unserved_num += 1
            return False
        elif (opt_veh_i == None):
            opt_veh_s.add(passenger)
            passenger.isShared()
        elif (opt_veh_s == None):
            status_request = opt_veh_i.assign(passenger)
            self.changeVehStatus(status_request)
        else:
            if (min_dist_s <= min_dist_i):
                opt_veh_s.add(passenger)
                passenger.isShared()
            else:
                status_request = opt_veh_i.assign(passenger)
                self.changeVehStatus(status_request)
        self.served_num += 1
        return True

    # batching assignment to serve a group of passenger 
    def batch_serve(self, passengers:list, r=math.inf):
        inf = 4000
        # bi direction map between nparray idx and veh
        valid_vehs = {}
        idx1 = 0
        for idle_veh in self.vehs_group[2]:
            valid_vehs[idx1], valid_vehs[idle_veh] = idle_veh, idx1
            idx1 += 1
        weight_table = inf * np.ones((len(passengers), int(len(valid_vehs)/2)))
        # bi direction map between nparray idx and pax
        valid_paxs = {}
        for idx2, pax in enumerate(passengers):
            for idle_veh in self.vehs_group[2]:
                dist = self.dist(idle_veh, pax, 1)
                # if there is no connecting path, the weight is still inf
                if dist == -1 or dist > r:
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
        unserved = []    
        for i, pax in enumerate(passengers):
            if not decision_table[i]:
                unserved.append(pax)
        # self.unserved_num += len(passengers) - served_num
        # self.served_num += served_num
        return unserved

    # function to return total driving distance, assigned time, inservice time
    def homo_info(self):
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

    # function to return location of each status group
    def sketch_helper(self):
        # key is status, value is location list
        sketch_table = []
        for status in range(len(self.status_table)):
            sketch_table.append([[], []])
            for veh in self.vehs_group[status]:
                sketch_table[status][0].append(veh.location()[0])
                sketch_table[status][1].append(veh.location()[1])
        return sketch_table