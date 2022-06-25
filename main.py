import random
from taxi_simul.simulation import Simulation
from bus_simul.simulation_bus import Simulation_bus
from city import City
import xlsxwriter as xw

# city = City("real-world", node_file="node.xls", link_file="link.xls")
# city.read()
random.seed(2)
# city = City()
# s = Simulation(city, fleet_size=70, lmd=300, T=10)
# s1, s2 = s.status1, s.status2
# print(s.opt_data())
# print(s.error())
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
# f = 70
# l = 300
# max_detour = 60
# workbook = xw.Workbook("M{}_lmd{}_detour.xlsx".format(f, l))
# worksheet1 = workbook.add_worksheet()
# totalt1, totalt2, totalavg = [], [], []
# for i in range(1, max_detour+1):
#     s = Simulation(city, fleet_size=f, T=7, lmd=l)
#     s.sharing_serve(res=1/60/60,detour_percentage=i)
#     t1, t2, avg = s.passenger_data()
#     totalt1.append(t1)
#     totalt2.append(t2)
#     totalavg.append(avg)
# worksheet1.write(0, 0, "detour percentage")
# worksheet1.write(0, 1, "avg idle t")
# worksheet1.write(0, 2, "avg shared t")
# worksheet1.write(0, 3, "avg combined t")

# for i in range(len(totalt1)):
#     worksheet1.write(i+1, 0, i+1)
#     worksheet1.write(i+1, 1, totalt1[i])
#     worksheet1.write(i+1, 2, totalt2[i])
#     worksheet1.write(i+1, 3, totalavg[i])
# workbook.close()


# city = City(type_name="Manhattan")
# f = 70
# l = 300
# s = Simulation(city, fleet_size=f, T=10, lmd=l)
# s.sharing_serve(res=1/60/60, detour_percentage=10)
# (s1, s2, s3), (t1, t2, t3) = s.passenger_data()

# def func(l:list, dx:float):
#     l.sort()
#     max_range = l[-1] - l[0] 
#     left = 0
#     curr = 0
#     distri = []
#     while curr < len(l)-1:
#         count = 0
#         while l[curr] <= left:
#             count += 1
#             curr += 1
#         distri.append((left, left+dx, count))
#         left += dx
#     return distri
# dx = 0.5/60
# distri1, distri2, distri3 = func(s1, dx), func(s2, dx), func(s2, dx)


# workbook = xw.Workbook("M{}_lmd{}_freq.xlsx".format(f, l))
# worksheet1 = workbook.add_worksheet("Idle ta")
# worksheet2 = workbook.add_worksheet("Shared ta")
# worksheet3 = workbook.add_worksheet("Total ta")
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
# workbook.close()