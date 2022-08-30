from fleet import Fleet
from city import City
from taxi import Taxi
from passenger import Passenger
import math

class Taxifleet(Fleet):
    # fleet_m[i][j] = fleet_size
    def __init__(self, fleet_m, id, city:City):
        super().__init__(id)    
        self.city = city
        n = len(fleet_m)
        if n != city.n:
            print("Error in matrix dimension")
            return     
        self.zone_group = {}
        for i in range(city.n**2):
            self.zone_group[i] = {}
        idle_status = (zone.id, -1, -1, -1)
        self.addVehGroup(idle_status)
        # assign taxi to each zone
        for i in range(n):
            for j in range(n):
                fleet_size = fleet_m[i][j]
                zone = city.zone_matrix[i][j]
                for k in range(fleet_size):
                    veh = Taxi((zone.id, k), zone, city, idle_status)
                    self.vehicles[veh.id] = veh 
                    self.vehs_group[idle_status].add(veh)
                    self.zone_group[zone.id][(-1, -1, -1)] = set(veh)

    # change veh's status from status1 to status2 
    # the input is the same as changeVehStatus
    def changeZoneStatus(self, status_request:tuple):
        if status_request == None:
            return 
        veh_id, status1, status2 = status_request
        if status1 == status2:
            return
        # split the status (s0, s1, s2, s3) into s0, (s1, s2, s3)
        i, status1 = status1[0], (status1[1], status1[2], status1[3])
        j, status2 = status2[0], (status2[1], status2[2], status2[3])
        veh = self.vehicles[veh_id]
        if status2 not in self.zone_group[j]:
            self.zone_group[j][status2] = set() 
        set_out, set_in = self.zone_group[i][status1], self.zone_group[j][status2]
        set_out.remove(veh)
        set_in.add(veh)
        return 

    # dist_type is [1: assigned distance, 2: service distance, 3:total distance]
    def dist(self, vehicle:Taxi, passenger:Passenger, dist_type:int):
        i_table = {1:[1, 0], 2:[0, 1], 3:[1, 1]} 
        i1, i2 = i_table[dist_type]
        dist = i1*(abs(vehicle.x - passenger.x) + abs(vehicle.y - passenger.y)) \
            +  i2*(abs(passenger.x - passenger.dx) + abs(passenger.y - passenger.dy))
        return dist
    
    # convert status (s0, s1, s2, s3) to 0/1/2/3 (idle/assigned/in service/rebalancing)
    def convertStatus(self, status):
        (s0, s1, s2, s3) = status
        # idle status
        if s1 == -1 and s2 == -1 and s3 == -1:
            return 0
        # assigned status
        elif s1 != -1:
            return 1
        # in service status
        elif s1 == -1 and s2 != -1:        
            return 2
        # rebalance status
        else:
            return 3
        
    # function to return location of each status group
    def sketch_helper(self):
        # key is status, value is location list
        sketch_table = []
        for status in range(4):
            sketch_table.append([[], []])
        for status in self.vehs_group:
            converted = self.convertStatus(status)
            for veh in self.vehs_group[status]:
                sketch_table[converted][0].append(veh.location()[0])
                sketch_table[converted][1].append(veh.location()[1])
        return sketch_table
    

    def serve(self, passenger:Passenger):
        c_oxy, c_dxy = passenger.location()
        ozone, dzone = passenger.zone, passenger.target_zone
        opt_veh, opt_dist = None, None
        # intrazonal caller
        if ozone.id == dzone.id:
            xlim1, ylim1, xlim2, ylim2 = self.city.feasibleZone_1(c_oxy, c_dxy, ozone.id)
            fz = self.city.feasibleZone_3(c_oxy, c_dxy, ozone.id)
            opt_veh0, opt_veh1, opt_veh3 = None, None, None
            dist0, dist1, dist3 = 2*self.city.length, 2*self.city.length, 2*self.city.length
            for status in self.zone_group[ozone.id]:
                (s1, s2, s3) = status
                # idle veh 
                if s1 == -1 and s2 == -1 and s3 == -1:
                    for idle_veh in self.zone_group[ozone.id][status]:
                        dist = self.dist(idle_veh, passenger, 1)
                        if dist < dist0:
                            opt_veh0, dist0 
                # delivering status with one pax 
                elif s1 == -1 and s2 != -1 and s3 == -1:
                    for veh in self.zone_group[ozone.id][status]:
                        # feasible zone of Case 1 intra intra (p v)
                        if (ozone.id == s2) and \
                            ((xlim1[0] <= veh.x and veh.x <= xlim1[1] and ylim1[0] <= veh.y and veh.y <= ylim1[1]) or\
                             (xlim2[0] <= veh.x and veh.x <= xlim2[1] and ylim2[0] <= veh.y and veh.y <= ylim2[1])):  
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist1:
                                opt_veh1, dist1 = veh, dist
                        # feasible zone of Case 3 intra inter (p v)
                        elif ozone.id != s2 and s2 in fz:
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist3:
                                opt_veh3, dist3 = veh, dist
            opt_veh, opt_dist = min([(opt_veh0, dist0), (opt_veh1, dist1), (opt_veh3, dist3)], key=lambda k : k[1])
        else:
            fz = self.city.feasibleZone_2(ozone.id, dzone.id)
            xlim, ylim = self.city.feasibleZone_4(c_oxy, ozone.id, dzone.id)
            opt_veh0, opt_veh2, opt_veh4 = None, None, None
            dist0, dist2, dist4 = 2*self.city.length, 2*self.city.length, 2*self.city.length
            for status in self.zone_group[ozone.id]:
                (s1, s2, s3) = status
                # idle veh 
                if s1 == -1 and s2 == -1 and s3 == -1:
                    for idle_veh in self.zone_group[ozone.id][status]:
                        dist = self.dist(idle_veh, passenger, 1)
                        if dist < dist0:
                            opt_veh0, dist0 

                elif s1 == -1 and s2 != -1 and s3 == -1:
                    for veh in self.zone_group[ozone.id][status]:
                        # feasible zone of Case 2 inter inter (p v)
                        if ozone.id != s2 and s2 in fz:  
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist2:
                                opt_veh2, dist2 = veh, dist
                        # feasible zone of Case 4 inter intra (p v)
                        elif ozone.id == s2 and \
                            (xlim[0] <= veh.x and veh.x <= xlim[1] and ylim[0] <= veh.y and veh.y <= ylim[1]):
                            dist = self.dist(veh, passenger, 1)
                            if dist < dist4:
                                opt_veh4, dist4 = veh, dist
            opt_veh, opt_dist = min([(opt_veh0, dist0), (opt_veh2, dist2), (opt_veh4, dist4)], key=lambda k : k[1])
        
        if opt_veh is None:
            passenger.status = -1
            return False   
        status_request = opt_veh.assign(passenger)
        self.changeVehStatus(status_request)
        self.changeZoneStatus(status_request)
        return True
