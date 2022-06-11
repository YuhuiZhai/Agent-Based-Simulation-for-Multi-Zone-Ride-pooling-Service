from city import City
from fleet import Fleet
from eventQueue import EventQueue
import utils
class Simulation_bus:
    def __init__(self, city:City, T:float, lmd:float, fleet_size:int, simul_type=""):
        self.clock = 0
        self.T = T
        self.fleet = {}
        self.events = {}
        self.simu_type = simul_type if simul_type in ["homogeneous", "heterogeneous"] else "homogeneous" 
        if self.simu_type == "homogeneous":
            self.city = city
            self.lmd = lmd
            self.fleet_size = fleet_size if fleet_size != None else 1.5*utils.optimal(self.city, self.lmd)[4]
            self.fleet[0] = Fleet(fleet_size, city, 0)
            self.events[0] = EventQueue(city, T, lmd, 0)
        
