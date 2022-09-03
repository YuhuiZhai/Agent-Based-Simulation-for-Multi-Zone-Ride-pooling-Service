from simulation import Simulation
from city import City

city1 = City("Manhattan")
s1 = Simulation(city1, fleet_size=20, lmd=50, T=10, lr=False, swap=False)
s1.sharing_serve(res=1/3600, detour_dist=1)


