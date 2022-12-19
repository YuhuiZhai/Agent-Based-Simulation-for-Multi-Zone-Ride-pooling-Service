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
        # lmd_m[i].append(1000)
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
# print("-------1-------")
# fleet_m = [[371, 306], [1417, 371]]
# rebalance_m[2][0] = 488.6259848
# rebalance_m[2][1] = 556.7415087
# rebalance_m[2][3] = 488.6437151

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 2
# print("-------2-------")
# fleet_m = [[383, 318], [1456, 382]]
# rebalance_m[2][0] = 500.2304038
# rebalance_m[2][1] = 562.5974402
# rebalance_m[2][3] = 500.2304038

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 3
# print("-------3-------")
# fleet_m = [[392, 330], [1501, 392]]
# rebalance_m[2][0] = 511.9703246
# rebalance_m[2][1] = 575.0216452
# rebalance_m[2][3] = 511.9703246

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 4
# print("-------4-------")
# fleet_m = [[401, 341], [1545, 401]]
# rebalance_m[2][0] = 522.925799
# rebalance_m[2][1] = 589.1483126
# rebalance_m[2][3] = 522.925799

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 5
# print("-------5-------")
# fleet_m = [[441, 394], [1760, 441]]
# rebalance_m[2][0] = 567.3882706
# rebalance_m[2][1] = 655.3127326
# rebalance_m[2][3] = 567.3882706

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 6
# print("-------6-------")
# fleet_m = [[511, 495], [2159, 511]]
# rebalance_m[2][0] = 631.0322965
# rebalance_m[2][1] = 748.4383004
# rebalance_m[2][3] = 631.0322965

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 7
# print("-------7-------")
# fleet_m = [[578, 593], [2536, 578]]
# rebalance_m[2][0] = 679.0846459
# rebalance_m[2][1] = 810.7437538
# rebalance_m[2][3] = 679.0846459

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 8
# print("-------8-------")
# fleet_m = [[643, 690], [2900, 643]]
# rebalance_m[2][0] = 718.0739786
# rebalance_m[2][1] = 856.291429
# rebalance_m[2][3] = 718.0739786

# city = City(length=10, n=2, max_v=25)
# s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
# s.simple_serve()
# s.export_passenger_time()
# s.export_P_over_lambda()
# s.export_state_number()

# 9
fleet_m = [[701, 784], [3256, 701]]
rebalance_m[2][0] = 757.4055
rebalance_m[2][1] = 894.7267
rebalance_m[2][3] = 701.2327
print(rebalance_m)
city = City(length=10, n=2, max_v=25)
s = Simulation(city=city, dt=1/3600, T=10, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)
s.simple_serve()
s.export_passenger_time(vd = True)
s.export_P_over_lambda()
s.export_state_number()



