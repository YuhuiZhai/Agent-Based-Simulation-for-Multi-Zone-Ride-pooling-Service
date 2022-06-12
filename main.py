import random
from taxi_simul.simulation import Simulation
from bus_simul.simulation_bus import Simulation_bus
from city import City

# city = City("real-world", node_file="node.xls", link_file="link.xls")
# city.read()
random.seed(2)
# city = City()
# simple assignment part
# simulation1 = Simulation(city, fleet_size=50, T=1, lmd=50)
# simulation1.simple_serve(res=1/60/60)
# simulation1.error()
# simulation1.export(name="simple", path="C:/22 Summer/week 4")

# batch assignment part
# simulation1.batch_serve(res=1/60/60, dt=1/6)
# simulation1.export("batch")

# share assignment
# simulation1.sharing_serve(res=1/60/60, detour_percentage=0.05)
# simulation1.export("share")

# animation part
# simulation1.make_animation(compression=25, fps=15)

# hetergeneous part
# city = City(length=3.6)
# a = [[500, 5], [5, 50]]
# b = [[8, 8], [8, 100]]
# simulation2 = Simulation(city, simul_type="heterogeneous", inter=True, T=1, lmd_map=a, fleet_map=b)
# simulation2.simple_serve(res=1/60/60)
# simulation2.export()
# simulation2.make_animation(compression=20, fps=15)

# city = City(type_name="Manhattan")
# ta, ts, na, ns, ni = [], [], [], [], []
# ta = []
# for i in range(1, 120):
#     s = Simulation(city, fleet_size=50, T=5, lmd=200)
#     s.batch_serve(res=1/60/60, dt=i/3600)
    # avg_ta, avg_ts, avg_na, avg_ns, avg_ni = s.fleet_info()
    # ta.append(avg_ta)
    # ts.append(avg_ts)
    # na.append(avg_na)
    # ns.append(avg_ns)
    # ni.append(avg_ni)
    # avg_ta = s.passenger_data()
    # ta.append(avg_ta)

# utils.zip_csv(["ta", "ts", "na", "ns", "ni"], [ta, ts, na, ns, ni], name="batch servre analysis")
# utils.zip_csv(["ta"], [ta], name="pax_analysis")

# random.seed(2)
city = City(length=4)
simulation = Simulation_bus(city, T=2, lmd=200, fleet_size=5)
simulation.Route1(res=1/3600)
simulation.make_animation(compression=40, fps=15)
