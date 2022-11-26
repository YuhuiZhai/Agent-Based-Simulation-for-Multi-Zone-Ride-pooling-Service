from simulation import Simulation
from city import City
lmd_m = []
rebalance_m = []
prob_matrix = []
for i in range(4):
    lmd_m.append([])
    rebalance_m.append([])
    prob_matrix.append([])
    for j in range(4):
        if j == 2:
            lmd_m[i].append(1400)
        else:
            lmd_m[i].append(200)
        rebalance_m[i].append(0)

fleet_m = [[706, 787], [3254, 706]]
rebalance_m[2][0] = 750.7914738
rebalance_m[2][1] = 891.4509837
rebalance_m[2][3] = 750.7914738
city = City(length=10, n=2, max_v=25)
s = Simulation(city=city, dt=1/3600, T=1, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
s.simple_serve()
s.export_deliver_time()
