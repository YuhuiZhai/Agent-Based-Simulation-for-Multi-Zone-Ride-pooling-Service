import numpy as np
from city import City
from fleet_taxi import Taxifleet
from eventQueue import EventQueue
from tqdm import tqdm
from animation import Animation
import xlsxwriter as xw
import openpyxl as op
import os
class Simulation:
    def __init__(self, city:City, dt:float, T:float, lmd_matrix=None, fleet_matrix=None, rebalance_matrix=None):
        self.clock, self.city, self.dt, self.T = 0, city, dt, T
        self.city.assignT(T)
        self.lmd_m, self.fleet_m, self.rebalance_m = lmd_matrix, fleet_matrix, rebalance_matrix
        self.fleet = Taxifleet(self.fleet_m, 0, self.city, self.dt, self.T, self.rebalance_m)
        self.events = EventQueue(T, self.lmd_m, 0, self.city)
        self.timeline = None
        self.fleet_info = [] # list of [ax, ay], [sx, sy], [ix, iy]
        self.passenger_info = [] # list of [px, py]
        self.city_number = self.city.n**2 

        # 3 dimensional list storing the traveling time of passenger 
        self.traveling_ts = [[[[], []] for j in range(self.city_number)] for i in range(self.city_number)]
        # double dictionary for state number and transition rate, just like fleet.zone_group
        self.status_record = {i:{} for i in range(self.city_number)}
        self.idx = 0

        # record of vehicle positions
        self.avg_position = {}
        # record of expected deliver time 
        self.deliver_time_table, self.deliver_count_table = {}, {}
        # record of flow transition, representing [a, b, c, d, g, p]
        self.flow_table = [{}, {}, {}, {}, {}, {}]
        # record of total weighted state number P
        self.Ps = []
        
        # dictionary storing unserved number of passenger
        self.unserved_number = {i:0 for i in range(self.city_number)}
        # record of unserved information [info = [starting time, ozone, dzone, direction, ni0i0, sum_ni0j0]]
        self.unserved_record = []
        
    
    def move(self):
        self.clock += self.dt
        self.fleet.zone_move(self.dt)
        self.events.move(self.dt)

    def simple_serve(self):
        self.timeline = np.arange(0, self.T, self.dt)
        for t in tqdm(self.timeline, desc="simple_serve loading"):
            p_id, p = self.events.head()
            while (not self.events.empty() and p.t_start < t):
                # unserved passenger exists
                opt_veh, dist, prev_status = self.fleet.serve(p)
                if opt_veh == None:
                    self.update_unserved(p)
                self.update_flow_table(0, prev_status)
                self.events.dequeue()
                p_id, p = self.events.head()
            self.fleet.rebalance()
            self.move()
            self.update()
        return 


    def test_simple_taxi(self):
        test_sample = 0
        count = 0
        for i in self.fleet.vehicles:
            if count > 3:
                break
            test_sample = self.fleet.vehicles[i]
            print(test_sample.status_distance_table)
            result = test_sample.get_status_distance()
            print(result)
            count += 1
        return 

    def update_unserved(self, passenger):
        self.unserved_number[passenger.zone.id] += 1 
        # record is a list [starting time, ozone, dzone, direction, ni0i0, sum_ni0j0]
        record = ["" for i in range(6)]
        record[0] = passenger.t_start
        O, D, = passenger.odzone()
        record[1], record[2] = O, D
        if O == D: record[3] = self.city.direction_helper(*passenger.location())
        if O not in self.status_record: 
            record[4], record[5] = 0, 0
        else:
            ni0i0 = self.status_record[O][(-1, O, -1)][-1] if (-1, O, -1) in self.status_record[O] else 0
            sum_ni0j0 = 0
            for i in range(self.city_number):
                if i == O:continue
                ni0j0 = self.status_record[O][(-1, i, -1)][-1] if (-1, i, -1) in self.status_record[O] else 0
                sum_ni0j0 += ni0j0
            record[4], record[5] = ni0i0, sum_ni0j0
        self.unserved_record.append(record)
        return record

    def update_state_transition(self):
        for zone_id in self.fleet.zone_group:
            for status in self.fleet.zone_group[zone_id]:
                if status not in self.status_record[zone_id]:
                    self.status_record[zone_id][status] = [0 for i in range(self.idx)]
                self.status_record[zone_id][status].append(len(self.fleet.zone_group[zone_id][status]))
        return
    
    def update_flow_table(self, type:int, status):
        if status == None:
            return 
        if status not in self.flow_table[type]:
            self.flow_table[type][status] = [0 for i in range(self.idx)]
        while len(self.flow_table[type][status]) < self.idx:
            self.flow_table[type][status].append(0)
        if len(self.flow_table) == self.idx:
            self.flow_table[type][status].append(1)
        else: 
            self.flow_table[type][status][-1] += 1
        return 

    def update_flow(self):
        # 0:a, 1:b, 2:c, 3:d, 4:g, 5:p
        for veh_id in self.fleet.vehicles:
            veh = self.fleet.vehicles[veh_id]
            prev_status = veh.prev_status
            curr_status = veh.status
            if prev_status == None or prev_status == curr_status:
                continue
            ps0, ps1, ps2, ps3 = prev_status
            cs0, cs1, cs2, cs3 = curr_status
            # status (j, i, -1, -1)
            if ps0 != ps1 and ps1 != -1 and ps2 == -1 and ps3 == -1:
                self.update_flow_table(1, prev_status)

            # status (i, -1, -1, -1) *
            elif ps1 == -1 and ps2 == -1 and ps3 == -1:
                # bij00 *
                if cs0 != cs1:
                    self.update_flow_table(1, curr_status)
                # ai000 *
                else:
                    self.update_flow_table(0, prev_status)

            # status (i, -1, i, -1) *
            elif ps1 == -1 and ps2 == ps0 and ps3 == -1:
                # di0i0 *
                if cs2 == -1:
                    self.update_flow_table(3, prev_status)
                # ai0i0 *
                else:
                    self.update_flow_table(0, prev_status)
            # status (i, -1, j, -1) * 
            elif ps1 == -1 and ps2 != -1 and ps2 != ps0 and ps3 == -1:
                # ai0j0 *
                if cs0 == cs1: 
                    self.update_flow_table(0, prev_status)
                # gi0j0 *
                if cs0 != ps0 and cs2 == ps2: 
                    self.update_flow_table(4, prev_status)
                    self.update_flow_table(2, curr_status)

            # status (i, i, -1 or i or j, -1) *
            elif ps0 == ps1 and ps3 == -1: 
                # piij0_j *
                if cs2 == ps2:
                    self.update_flow_table(5, (*prev_status, cs3))
                else:
                    self.update_flow_table(5, (*prev_status, cs2))
            
            # status (i, -1, i, k) *
            elif ps0 == ps2 and ps1 == -1 and ps3 != -1:
                self.update_flow_table(3, prev_status)
            
            # status (i, -1, j, k) *
            elif ps1 == -1 and ps0 != ps2 and ps2 != -1 and ps3 != -1:
                # gi0jk and ci0jk *
                self.update_flow_table(4, prev_status)
                self.update_flow_table(2, curr_status)
        return 

    def update_P(self):
        P = self.fleet.computeP()
        self.Ps.append(P)
        
    def update_pos(self):
        for status in self.fleet.vehs_group:
            vehx, vehy = [], [] 
            for veh in self.fleet.vehs_group[status]:
                vehx.append(veh.x)
                vehy.append(veh.y)
            vehx = sum(vehx)/len(vehx) if len(vehx) != 0 else None
            vehy = sum(vehy)/len(vehy) if len(vehy) != 0 else None
            if status not in self.avg_position:
                self.avg_position[status] = [(None, None) for i in range(self.idx)]
            self.avg_position[status].append((vehx, vehy))
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
        self.update_pos()
        self.update_flow()
        self.update_P()
        self.idx += 1
        return 

    def make_animation(self, compression=50, fps=15, name="simulation", path=""):
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
        return 

    def export_avg_position(self, status=[(2,-1,2,-1)], name=""):
        workbook = xw.Workbook(f"{self.fleet_m}_avg_position.xlsx")
        for s in status:
            worksheet = workbook.add_worksheet(f"{s}")
            worksheet.write(0, 0, "avg_x")
            worksheet.write(0, 1, "avg_y")
            worksheet.write(3, 0, "idx")
            worksheet.write(3, 1, "avg_x")
            worksheet.write(3, 2, "avg_y")
            xsum, ysum = 0, 0
            xlen, ylen = 0, 0
            for idx, pos in enumerate(self.avg_position[s]):
                x, y = pos
                if x == None or y == None:
                    continue
                worksheet.write(3+idx, 0, idx*self.dt)
                worksheet.write(3+idx, 1, x)
                worksheet.write(3+idx, 2, y)
                xsum += x; ysum += y; xlen += 1; ylen += 1
            worksheet.write(1, 0, xsum / xlen)
            worksheet.write(1, 1, ysum / ylen)
        workbook.close()
        return 

    def export_valid_i0i0_1(self):
        ratio_m = []
        for zone_id in self.fleet.valid_i0i0s_1:
            temp = []
            for i in self.fleet.valid_i0i0s_1[zone_id]:
                valid_num, total_num = i
                if total_num <= 0 :
                    continue
                ratio = valid_num / total_num
                temp.append(ratio)
            avg = sum(temp) / len(temp)
            ratio_m.append(avg)
        print(ratio_m)
        return ratio_m

    def export_valid_i0i0_4(self):
        ratio_m = []
        ratio_m_diag = []
        distx, disty = [], []

        for zone_id in self.fleet.valid_i0i0s_4:
            temp = []
            for idx, i in enumerate(self.fleet.valid_i0i0s_4[zone_id]):
                if idx <= 1/3*len(self.fleet.valid_i0i0s_4[zone_id]):
                    continue
                valid_num, total_num = i
                if total_num <= 0 :
                    continue
                ratio = valid_num / total_num
                temp.append(ratio)
            avg = sum(temp) / len(temp)
            ratio_m.append(avg)
        for zone_id in self.fleet.valid_i0i0s_4_diag:
            temp = []
            for i in self.fleet.valid_i0i0s_4_diag[zone_id]:
                if idx <= 1/3*len(self.fleet.valid_i0i0s_4_diag[zone_id]):
                    continue
                valid_num, total_num = i
                if total_num <= 0 :
                    continue
                ratio = valid_num / total_num
                temp.append(ratio)
            avg = sum(temp) / len(temp)
            ratio_m_diag.append(avg)
        print("NEWS : ", ratio_m)
        print("diagnoal : ", ratio_m_diag)
        return ratio_m, ratio_m_diag
    
    def export_assigned_dist(self):
        count = 0
        num = 0
        for veh_id in self.fleet.vehicles:
            veh = self.fleet.vehicles[veh_id]
            count += sum(veh.assigned_dist_record)
            num += len(veh.assigned_dist_record)
        avg_assigned_dist = count / num
        return avg_assigned_dist

    def export_P_over_lambda(self):
        Ps = self.Ps[int(len(self.Ps)/3):]
        avg_P = sum(Ps) / len(Ps)
        total_lambda = sum(np.array(self.lmd_m).flatten())
        print(avg_P / total_lambda)
        return avg_P / total_lambda
 
    def export_flow(self, full=False):
        temp = {0:"a", 1:"b", 2:"c", 3:"d", 4:"g", 5:"p"}
        workbook = xw.Workbook(f"{self.fleet_m}_flow.xlsx")
        worksheet0 = workbook.add_worksheet("summary")
        worksheets = []
        for i in range(6):
            worksheet0.write(0, i*2, f"{temp[i]}_xxxx")
            if full:
                worksheet = workbook.add_worksheet(temp[i])
                worksheet.write(0, 0, "time")
                for j in range(self.idx):
                    worksheet.write(j+1, 0, j*self.dt)
            flows = self.flow_table[i]
            for j, status in enumerate(flows):
                worksheet0.write(j+1, i*2, f"{temp[i]}_{status}")
                worksheet0.write(j+1, i*2+1, sum(flows[status])/self.idx/self.dt)
                if full:
                    worksheet.write(0, j+1, f"{temp[i], status}")
                    for k in range(self.idx):
                        if k >= len(flows[status]):
                            worksheet.write(k+1, j+1, 0)
                        else:
                            worksheet.write(k+1, j+1, flows[status][k])
        workbook.close()
        return

    # export state transition information 
    def export_state_number(self, full=False, shift=1):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_exist = os.path.exists(f"{dir_path}\state_number")
        if not path_exist:
            os.makedirs(f"{dir_path}\state_number")
        workbook = xw.Workbook(f"{dir_path}\state_number\{self.fleet_m}_state_number.xlsx")
        cell_format = workbook.add_format()
        cell_format.set_bold()
        cell_format.set_font_color('red')
        worksheet0 = workbook.add_worksheet("summary")
        worksheet0.write(0, 0, "status")
        worksheet0.write(0, 1, "avg number")
        if full:
            worksheet1 = workbook.add_worksheet("status number")
        worksheet2 = workbook.add_worksheet("unserved number")
        row = 1
        for zone_id in self.status_record:
            for status in self.status_record[zone_id]:
                l = len(self.status_record[zone_id][status])
                # get rid of warming stage
                avg = sum(self.status_record[zone_id][status][int(1/3*l):]) / len(self.status_record[zone_id][status][int(1/3*l):]) 
                if status == (-1, -1, -1):
                    worksheet0.write(row, 0, f"n_{zone_id+shift}{status[0]+shift}{status[1]+shift}{status[2]+shift}", cell_format)
                else:
                    worksheet0.write(row, 0, f"n_{zone_id+shift}{status[0]+shift}{status[1]+shift}{status[2]+shift}")
                worksheet0.write(row, 1, avg)
                row += 1
        if full:
            for i in range(self.idx):
                worksheet1.write(i+1, 0, i*self.dt)
            worksheet1.write(0, 0, "time t (s)")
            col = 1
            for zone_id in self.status_record:
                for status in self.status_record[zone_id]:
                    worksheet1.write(0, col, f"({zone_id, *status}")
                    row = 1
                    for num in self.status_record[zone_id][status]:
                        worksheet1.write(row, col, num)
                        row += 1
                    col += 1
        worksheet2.write(0, 0, "unserved number in each zone")
        for i in range(self.city.n):
            for j in range(self.city.n):
                zone_id = i*self.city.n + j
                worksheet2.write(i+1, j, self.unserved_number[zone_id])   
        wb = workbook.add_worksheet("P")     
        wb.write(0, 0, "P/sum lamda")
        wb.write(0, 1, self.export_P_over_lambda())
        workbook.close()
        return 

    def export_passenger_time(self, full=False):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_exist = os.path.exists(f"{dir_path}\passenger_time")
        if not path_exist:
            os.makedirs(f"{dir_path}\passenger_time")
        for info in self.events.queue:
            p = info[1]
            if p.t_start <= self.T*1/3:
                continue
            # if p.status == -1: 
            #     ozone = self.city.getZone(p.zone.id)
            #     dzone = self.city.getZone(p.target_zone.id) 
            #     dist = abs(ozone.center[0]-dzone.center[0]) + abs(ozone.center[1]-dzone.center[1])
            #     self.traveling_ts[p.zone.id][p.target_zone.id][0].append((dist + self.city.l)/self.city.max_v)
            if p.status == 3:
                self.traveling_ts[p.zone.id][p.target_zone.id][p.rs_status].append(p.t_end - p.t_start)
        workbook = xw.Workbook(f"{dir_path}\passenger_time\{self.fleet_m}_travel_time.xlsx")
        worksheet0 = workbook.add_worksheet("passenger total traveling time")
        if full:
            worksheet1 = workbook.add_worksheet("passenger time of caller")
            worksheet2 = workbook.add_worksheet("passenger time of seeker")
            worksheet3 = workbook.add_worksheet("distance of choices")
            worksheet1.write(0, 0, "zone i \ zone j")
            worksheet2.write(0, 0, "zone i \ zone j")
            for i in range(self.city_number):
                worksheet1.write(0, i+1, f"{i}")
                worksheet1.write(i+1, 0, f"{i}")
                worksheet2.write(0, i+1, f"{i}")
                worksheet2.write(i+1, 0, f"{i}")
        total_sum, total_sum0, total_sum1 = 0, 0, 0
        total_num, total_num0, total_num1 = 0, 0, 0
        for i in range(self.city_number):
            for j in range(self.city_number):
                l0, l1 = len(self.traveling_ts[i][j][0]), len(self.traveling_ts[i][j][1])
                total_sum += (sum(self.traveling_ts[i][j][0]) + sum(self.traveling_ts[i][j][1]))
                total_sum0 += sum(self.traveling_ts[i][j][0])
                total_sum1 += sum(self.traveling_ts[i][j][1])
                total_num += (l0 + l1) 
                total_num0 += l0
                total_num1 += l1 
                avg0 = 0 if l0 == 0 else sum(self.traveling_ts[i][j][0])/l0
                avg1 = 0 if l1 == 0 else sum(self.traveling_ts[i][j][1])/l1
                if full:
                    worksheet1.write(i+1, j+1, avg0)
                    worksheet2.write(i+1, j+1, avg1)
        worksheet0.write(0, 0, "average passenger door to door traveling time (hr)")
        worksheet0.write(1, 0, total_sum/total_num)
        worksheet0.write(3, 0, "average caller door to door traveling time (hr)")
        worksheet0.write(4, 0, total_sum0/total_num0)
        worksheet0.write(6, 0, "average seeker door to door traveling time (hr)")
        worksheet0.write(7, 0, total_sum1/total_num1)
        if full:
            new_row_idx = self.city_number + 2
            worksheet1.write(new_row_idx, 0, "passenger travelling time distribution")
            worksheet2.write(new_row_idx, 0, "passenger travelling time distribution")
            idx = 0
            for i in range(self.city_number):
                for j in range(self.city_number):
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
            for i in range(self.city_number):
                for j in range(self.city_number):
                    dist_ij = dist_infos[(i, j)]
                    for info in dist_ij:
                        worksheet3.write(curr_row, 0, f"{(i, j)}")
                        for k in range(5):
                            worksheet3.write(curr_row, k+1, info[k])
                        curr_row += 1
        workbook.close()
        return 

    def export_uneserved_record(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_exist = os.path.exists(f"{dir_path}\info_unserved")
        if not path_exist:
            os.makedirs(f"{dir_path}\info_unserved")
        workbook = xw.Workbook(f"{dir_path}\info_unserved\{self.fleet_m}_unserved.xlsx")
        ws = [0 for i in range(self.city_number)]
        for i in range(self.city_number):
            ws[i] = workbook.add_worksheet(f"Zone_{i+1}")
            ws[i].write(0, 0, "Incoming time"); ws[i].write(0, 1, "Origin"); ws[i].write(0, 2, "Destination")
            ws[i].write(0, 3, "Direction"); ws[i].write(0, 4, "ni0i0"); ws[i].write(0, 5, "sum_ni0j0")
        row = [1 for i in range(self.city_number)]
        for i in self.unserved_record:
            zone_id = i[1]
            ws[zone_id].write(row[zone_id], 0, i[0]); ws[zone_id].write(row[zone_id], 1, i[1]); ws[zone_id].write(row[zone_id], 2, i[2])
            ws[zone_id].write(row[zone_id], 3, i[3]); ws[zone_id].write(row[zone_id], 4, i[4]); ws[zone_id].write(row[zone_id], 5, i[5])
            row[zone_id] += 1
        ws2 = workbook.add_worksheet("unserved number")
        ws2.write(0, 0, "unserved number in each zone")
        for i in range(self.city.n):
            for j in range(self.city.n):
                zone_id = i*self.city.n + j
                ws2.write(i+1, j, self.unserved_number[zone_id])   
        workbook.close()

    def export_delivery_distance(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_exist = os.path.exists(f"{dir_path}\delivery_distance")
        if not path_exist:
            os.makedirs(f"{dir_path}\delivery_distance")
        wb = xw.Workbook(f"{dir_path}\delivery_distance\{self.fleet_m}_delivery_distance.xlsx")
        avg_dist = []
        for veh_id in self.fleet.vehicles:
            veh = self.fleet.vehicles[veh_id]
            dist = veh.get_delivery_distance()
            # initialize the summary table
            if avg_dist == []:
                for j in range(self.city_number):
                    avg_dist.append({})
                    for i in dist[j]: 
                        avg_dist[j][i] = [0, 0]
            for j in range(self.city_number):
                for i in dist[j]: 
                    if dist[j][i] != None:
                        avg_dist[j][i][0] += dist[j][i]
                        avg_dist[j][i][1] += 1
        for j in range(self.city_number):
            for i in avg_dist[j]: 
                avg_dist[j][i] = avg_dist[j][i][0]/avg_dist[j][i][1] if avg_dist[j][i][1] != 0 else -1
        
        for j in range(self.city_number):
            ws = wb.add_worksheet(f"Zone_{j+1}")
            idx1_text = {0:f"{j+1}0{j+1}0", 1:f"{j+1}0{j+1}{j+1}", 2:f"{j+1}0j0", 3:f"{j+1}0{j+1}j", 4:f"{j+1}0jk"} 
            idx2_text = {n:f"Case{n+1}" for n in range(5)}
            for i in avg_dist[j]:
                col, row = i
                ws.write(0, col*2, idx1_text[col])
                ws.write(row+1, col*2, idx2_text[row])
                ws.write(row+1, col*2+1, avg_dist[j][i])
        wb.close()

            
             
            