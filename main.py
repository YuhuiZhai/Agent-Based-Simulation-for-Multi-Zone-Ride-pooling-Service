import random
from taxi_simul.simulation import Simulation
from bus_simul.simulation_bus import Simulation_bus
from city import City
import xlsxwriter as xw
import utils
import numpy as np
# city = City("real-world", node_file="node.xls", link_file="link.xls")
# city.read()
random.seed(2)
city = City()
s = Simulation(city, fleet_size=20, lmd=50, T=10)
s.simple_serve(res=1/3600)
s.make_animation(compression=20)

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
# f = 30
# l = 50
# max_detour = 1
# # max_batch = 60
# workbook = xw.Workbook("M{}_lmd{}_detour{}.xlsx".format(f, l, max_detour))
# worksheet1 = workbook.add_worksheet("1")
# worksheet2 = workbook.add_worksheet("2")
# totalt1, totalt2, totalavg = [], [], []
# mid1s, mid2s, mid3s = [], [], []
# avgtas = []
# for i in np.arange(0, max_detour, 0.05):
#     random.seed(2)
#     s = Simulation(city, fleet_size=f, T=10, lmd=l)
#     s.sharing_serve(res=1/3600, detour_dist=i)
#     (t1, t2, t3), (mid1, mid2, mid3) = s.passenger_data()[1], s.passenger_data()[2]
#     totalt1.append(t1)
#     totalt2.append(t2)
#     totalavg.append(t3)
#     mid1s.append(mid1)
#     mid2s.append(mid2)
#     mid3s.append(mid3)
# worksheet1.write(0, 0, "detour percentage")
# worksheet1.write(0, 1, "avg idle t")
# worksheet1.write(0, 2, "avg shared t")
# worksheet1.write(0, 3, "avg combined t")
# worksheet2.write(0, 0, "detour percentage")
# worksheet2.write(0, 1, "mid idle t")
# worksheet2.write(0, 2, "mid shared t")
# worksheet2.write(0, 3, "mid combined t")

# for i in range(len(totalt1)):
#     worksheet1.write(i+1, 0, i)
#     worksheet1.write(i+1, 1, totalt1[i])
#     worksheet1.write(i+1, 2, totalt2[i])
#     worksheet1.write(i+1, 3, totalavg[i])

# for i in range(len(mid1s)):
#     worksheet2.write(i+1, 0, i)
#     worksheet2.write(i+1, 1, mid1s[i])
#     worksheet2.write(i+1, 2, mid2s[i])
#     worksheet2.write(i+1, 3, mid3s[i])
# workbook.close()

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
