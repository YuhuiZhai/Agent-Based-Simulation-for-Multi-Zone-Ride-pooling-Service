from fleet import Fleet
from city import City
from bus_simul.bus import Bus

class Busfleet(Fleet):
    def __init__(self, n:int, city:City, id):
        super().__init__(n, city, id)   
        self.init_group(
            status_name={0:"stopping", 1:"driving"}
        )
        for i in range(n):
            veh = Bus((self.id, i), city, t0=i*15*60/3600)
            self.vehicles[(self.id, i)] = veh
            self.vehs_group[1].add(veh)
    
    # assign route to the fleet, which is list [stop_id]
    def addRoute(self, route:list):
        for veh_id in self.vehicles:
            veh = self.vehicles[veh_id]
            veh.route = route
    
