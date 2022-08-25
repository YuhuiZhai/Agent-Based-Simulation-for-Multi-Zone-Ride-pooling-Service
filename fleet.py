class Fleet:
    def __init__(self, n:int, id):
        self.fleet_size, self.id = n, id
        self.clock = 0
        self.vehicles = {}
        self.status_table = {}
        self.vehs_group = {}
        
    # status_name: dictionary of status, key is status, value is string_type name
    # status_num: initial number of status, key is status, value is any number
    def init_group(self, status_name:dict):
        self.status_table = status_name
        for status in status_name:
            self.vehs_group[status] = set()
        return 

    # function to check whether the status is already existed
    def in_group(self, status):
        return status in self.vehs_group

    # add a set of vehicles with a default status
    # status can be any type, in this case which is (s0, s1, s2, s3)
    def add_group(self, status):
        if self.in_group(status):
            print("Already exists")
            return 
        self.vehs_group[status] = set()
        return

    # change veh's status from status1 to status2 
    def changeVehStatus(self, status_request:tuple):
        if status_request == None:
            return 
        veh_id, status1, status2 = status_request
        if status1 == status2:
            return
        veh = self.vehicles[veh_id]
        if not self.in_group(status2):
            self.add_group(status2)
        set_out, set_in = self.vehs_group[status1], self.vehs_group[status2]
        set_out.remove(veh)
        set_in.add(veh)
        return 

    # function to serve the passenger at time t
    def move(self, dt):
        for id in self.vehicles:
            status_request = self.vehicles[id].move(dt)
            self.changeVehStatus(status_request)
        self.clock += dt
    
    # function for making animation
    def sketch_helper(self):
        sketch_table = []
        for status in range(len(self.status_table)):
            sketch_table.append([[], []])
            for veh in self.vehs_group[status]:
                sketch_table[status][0].append(veh.location()[0])
                sketch_table[status][1].append(veh.location()[1])
        return sketch_table