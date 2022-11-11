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
        prob_matrix[i].append([0, 0, 0, 0])
prob_matrix[0][1][1] = 1.0
prob_matrix[0][2][3] = 1.0
prob_matrix[0][3][1] = 0.5
prob_matrix[0][3][3] = 0.5
prob_matrix[1][0][2] = 1.0
prob_matrix[1][2][2] = 0.5
prob_matrix[1][2][3] = 0.5
prob_matrix[1][3][3] = 1.0
prob_matrix[2][0][0] = 1.0
prob_matrix[2][1][0] = 0.5
prob_matrix[2][1][1] = 0.5
prob_matrix[2][3][1] = 1.0
prob_matrix[3][0][0] = 0.5
prob_matrix[3][0][2] = 0.5
prob_matrix[3][1][0] = 1.0
prob_matrix[3][2][2] = 1.0

# 1
# fleet_m = [[482, 400], [1382, 482]]
# rebalance_m[2][0] = 666.71
# rebalance_m[2][1] = 644.95
# rebalance_m[2][3] = 666.71

# # 2
# fleet_m = [[596, 507], [1500, 596]]
# rebalance_m[2][0] = 753.27
# rebalance_m[2][1] = 737.45
# rebalance_m[2][3] = 753.27

# # 3
# fleet_m = [[705, 613], [1611, 705]]
# rebalance_m[2][0] = 809.48
# rebalance_m[2][1] = 800.33
# rebalance_m[2][3] = 809.48

# # 4
# fleet_m = [[812, 717], [1721, 812]]
# rebalance_m[2][0] = 850.91
# rebalance_m[2][1] = 846.79
# rebalance_m[2][3] = 850.91

# # 5
# fleet_m = [[918, 821], [1827, 918]]
# rebalance_m[2][0] = 883.34
# rebalance_m[2][1] = 882.87
# rebalance_m[2][3] = 883.3

# # 6
# fleet_m = [[1023, 923], [1933, 1023]]
# rebalance_m[2][0] = 909.68
# rebalance_m[2][1] = 911.88
# rebalance_m[2][3] = 909.68

# # 6
fleet_m = [[1126, 1025], [2037, 1126]]
rebalance_m[2][0] = 931.63
rebalance_m[2][1] = 935.78
rebalance_m[2][3] = 931.63

city = City(length=10, n=2, max_v=25)
s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
s.simple_serve()
s.export_passenger_time()
s.export_P_over_lambda()
s.export_state_number()

