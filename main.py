import random
from taxi_simul.simulation import Simulation
from bus_simul.simulation_bus import Simulation_bus
from city import City
import xlsxwriter as xw
import utils
import numpy as np
import matplotlib.pyplot as plt
import time 
# city = City("real-world", node_file="node.xls", link_file="link.xls")
# print(s.passenger_data()[1])
# print(s.passenger_data()[2])
# s.make_animation(compression=30)
# # s.export()
# s1, s2 = s.status1, s.status2
# workbook = xw.Workbook("double status.xlsx")
# worksheet1 = workbook.add_worksheet(name="positive status")
# worksheet2 = workbook.add_worksheet(name="negative status")
# worksheet1.write(0,0, "t")
# worksheet1.write(0,1, "na")
# worksheet1.write(0,2, "ns")
# worksheet1.write(0,3, "ni")
# worksheet2.write(0,0, "t")
# worksheet2.write(0,1, "na")
# worksheet2.write(0,2, "ns")
# worksheet2.write(0,3, "ni")
# for i in range(len(s.status1)):
#     worksheet1.write(i+1, 0, s1[i][0])
#     worksheet1.write(i+1, 1, s1[i][1])
#     worksheet1.write(i+1, 2, s1[i][2])
#     worksheet1.write(i+1, 3, s1[i][3])
# for i in range(len(s.status2)):
#     worksheet2.write(i+1, 0, s2[i][0])
#     worksheet2.write(i+1, 1, s2[i][1])
#     worksheet2.write(i+1, 2, s2[i][2])
#     worksheet2.write(i+1, 3, s2[i][3])
# workbook.close()


# hetergeneous part
# city = City(length=3.6)
# a = [[500, 5], [5, 50]]
# b = [[8, 8], [8, 100]]
# simulation2 = Simulation(city, simul_type="heterogeneous", inter=True, T=1, lmd_map=a, fleet_map=b)
# simulation2.simple_serve(res=1/60/60)
# simulation2.export()
# simulation2.make_animation(compression=20, fps=15)

# city = City()
# f, l = 20, 10
# s = Simulation(city, fleet_size=f, T=10, lmd=l)
# prob = s.batch_serve(res=1/3600, dt=1/60)
# workbook = xw.Workbook("prob_M{}_lmd{}.xlsx".format(f, l))
# worksheet = workbook.add_worksheet()
# worksheet.write(0, 0, "t")
# worksheet.write(0, 1, "successful_pair")
# worksheet.write(0, 2, "pax_num")
# worksheet.write(0, 3, "idle_num")
# worksheet.write(0, 4, "prob_pax")
# worksheet.write(0, 5, "prob_veh")
# for i in range(len(prob)):
#     worksheet.write(i+1, 0, prob[i][0])
#     worksheet.write(i+1, 1, prob[i][1])
#     worksheet.write(i+1, 2, prob[i][2])
#     worksheet.write(i+1, 3, prob[i][3])
#     worksheet.write(i+1, 4, prob[i][4])
#     worksheet.write(i+1, 5, prob[i][5])
# workbook.close()

# city = City(type_name="Manhattan")
# f_max = 44
# l = 200
# # max_detour = 2
# max_batch = 60
# workbook = xw.Workbook("M{}_lmd{}_detour{}.xlsx".format(f_max, l, max_batch))
# worksheet1 = workbook.add_worksheet("1")
# totalt1, totalt2, totalavg = [], [], []
# for i in np.arange(1, max_batch+1, 4):
#     totalt1.append([])
#     for f in np.arange(int(2/3)*f_max, f_max+1, 1):
#         random.seed(2)
#         s = Simulation(city, fleet_size=f, T=10, lmd=l)
#         # s.sharing_serve(res=1/3600, detour_dist=i)
#         s.batch_serve(res=1/3600, dt=i/3600)
#         (t1, t2, t3), (mid1, mid2, mid3) = s.passenger_data()[1], s.passenger_data()[2]
#         totalt1[-1].append(t1)
# worksheet1.write(0, 0, "batch gap \ fleet size")
# for i in range(len(totalt1)):
#     worksheet1.write(i+1, 0, i+1)
# for j in range(len(totalt1[0])):
#     worksheet1.write(0, j+1, j+1)
# for i in range(len(totalt1)):
#     for j in range(len(totalt1[i])):
#         worksheet1.write(i+1, j+1, totalt1[i][j])
# workbook.close()
# totalt1 = np.array(totalt1)
# im = plt.imshow(totalt1, interpolation='none')
# plt.colorbar(im, orientation='horizontal')  
# plt.show()
# random.seed(2)
# city = City(type_name="Manhattan")
# f = 200
# l = 1000
# s = Simulation(city, fleet_size=f, T=10, lmd=l)
# s.sharing_serve(res=1/60/60, detour_dist=0.5)
# (s1, s2, s3), (t1, t2, t3), (mid1, mid2, mid3) = s.passenger_data()
# dx = 5*1/3600
# distri1, distri2, distri3 = utils.func(s1, dx), utils.func(s2, dx), utils.func(s3, dx)
# workbook1 = xw.Workbook("M{}_lmd{}_freq.xlsx".format(f, l))
# worksheet1 = workbook1.add_worksheet("Idle ta")
# worksheet2 = workbook1.add_worksheet("Shared ta")
# worksheet3 = workbook1.add_worksheet("Total ta")
# worksheet1.write(0, 0, "Interval of ta")
# worksheet1.write(0, 1, "Idle ta ")
# worksheet2.write(0, 0, "Interval of ta")
# worksheet2.write(0, 1, "Shared ta ")
# worksheet3.write(0, 0, "Interval of ta")
# worksheet3.write(0, 1, "Total ta ")
# for i in range(len(distri1)):
#     worksheet1.write(i+1, 0, distri1[i][0])
#     worksheet1.write(i+1, 1, distri1[i][2])
# for i in range(len(distri2)):
#     worksheet2.write(i+1, 0, distri2[i][0])
#     worksheet2.write(i+1, 1, distri2[i][2])
# for i in range(len(distri3)):
#     worksheet3.write(i+1, 0, distri3[i][0])
#     worksheet3.write(i+1, 1, distri3[i][2])
# workbook1.close()
# workbook2 = xw.Workbook("M{}_lmd{}_distirbution.xlsx".format(f, l))
# worksheet1 = workbook2.add_worksheet("Idle ta")
# worksheet2 = workbook2.add_worksheet("Shared ta")
# worksheet3 = workbook2.add_worksheet("Total ta")
# worksheet1.write(0, 0, "idx")
# worksheet1.write(0, 1, "Idle ta ")
# worksheet2.write(0, 0, "idx")
# worksheet2.write(0, 1, "Shared ta ")
# worksheet3.write(0, 0, "idx")
# worksheet3.write(0, 1, "Total ta ")
# s1.sort()
# s2.sort()
# s3.sort()
# for i in range(len(s1)):
#     worksheet1.write(i+1, 0, i+1)
#     worksheet1.write(i+1, 1, s1[i])
# for i in range(len(s2)):
#     worksheet2.write(i+1, 0, i+1)
#     worksheet2.write(i+1, 1, s2[i])
# for i in range(len(s3)):
#     worksheet3.write(i+1, 0, i+1)
#     worksheet3.write(i+1, 1, s3[i])
# workbook2.close()
# start = time.time()

city1 = City("Manhattan")
s1 = Simulation(city1, fleet_size=1800, lmd=10000, T=10, lr=False,swap=True)
s1.batch_serve(res=1/3600, dt=5/3600)
print(s1.passenger_data()[1])

