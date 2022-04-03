from vehicle import Vehicle
import math 
import utils 
from tqdm import tqdm 
class Fleet:
    def __init__(self, n, city, connected):
        self.clock = 0
        self.fleet_size = n
        self.vehicles = {}
        self.unserved = []
        for i in tqdm(range(n), desc="Fleet"):
            self.vehicles[i] = Vehicle(i, city, connected)

    def move(self, dt):
        for vehicle in self.vehicles:
            if self.vehicles[vehicle].status != 'idle':
                [temp_number, temp_time] = self.vehicles[vehicle].move(dt)
        self.clock += dt

    def serve(self, passenger):
        min_dist_empty = math.inf
        empty = None

        for vehicle in self.vehicles:
            if self.vehicles[vehicle].status == 'in-service':
                pass
            else:
                if self.vehicles[vehicle].status == 'assigned':
                    pass
                else:
                    temp_dist = utils.dist(city, self.vehicles[vehicle].node, self.vehicles[vehicle].len, passenger.o_node, passenger.o_len)
                    if temp_dist < min_dist_empty:
                        min_dist_empty = temp_dist
                        empty = vehicle
                        #extra_time = 0

        if empty is None:
            self.unserved.append(passenger)
            return None
        else:
            self.vehicles[empty].assign(passenger)
            return empty

