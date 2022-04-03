import utils 
class Vehicle:
    def __init__(self, vehicle_id, city, connected):
        self.city = city
        self.id = vehicle_id
        self.clock = 0
        self.node, self.len = utils.generate_location(city, connected)
        self.speed = 1
        self.load = 0
        self.status = 'idle' #assigned #in-service
        self.passenger = None
        # distance of passenger's destination from link's origin node
        self.plen = None
        # ordered list of passed nodes [..., cityNode1, cityNode2, cityNode3, ...]
        self.path = [] 

    # move along the path and update the location of vehicle
    def move(self, dt):
        if dt <= 0 or self.path is None:
            print("stop moving")
            return 
        # edge case last citylink
        if len(self.path) == 1:
            temp = self.len + dt * self.speed
            # driving over destination
            if (temp > self.plen):
                self.path.pop()
                self.len = self.plen
        else:
            self.len += dt * self.speed
            if (self.len > self.node.length):
                self.path.pop()
                # id of next link  
                next_id = self.city.map[self.path[0], self.path[1]]
                self.node = self.city.links[next_id]
                self.len = 0
        self.clock += dt

    def assign(self, city, passenger):
        if self.load > 1:
            print('error: too many passengers on vehicle', self.id)
            return        
        self.load += 1
        self.passenger = passenger
        self.plen = passenger.d_len
        self.status = 'assigned'
        # assign current location to passenger and passenger origin to destination
        self.path = self.path + city.dj_path[self.node, passenger.o_node][1] + city.dj_path[passenger.o_node, passenger.d_node][1]
        return


    def deliver(self):
        self.load -= 1
        if self.load < 0:
            print('error: negative passengers on one vehicle\n')
        else:
            self.passenger = None
            if self.load == 0:
                self.status = 'idle'

    def xy(self, city):
        ox = city.links[self.node.id].ox
        oy = city.links[self.node.id].oy
        dx = city.links[self.node.id].dx
        dy = city.links[self.node.id].dy
        diff_x = dx-ox
        diff_y = dy-oy
        if city.links[self.node.id].length == 0:
            print("link length = 0:")
            print(self.node.id)
            return ox, oy
        else:
            percentage = self.len/city.links[self.node.id].length
            return ox+percentage*diff_x, oy+percentage*diff_y


