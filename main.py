import xlrd
import random 
from cityNode import CityNode
from cityLink import CityLink
from city import City
from fleet import Fleet
from linkedList import LinkedList
from status import Status
from passenger import Passenger
from eventQueue import EventQueue
from vehicle import Vehicle
from node import Node
import utils 
import matplotlib.pyplot as plt


random.seed(2)
# input city information
city = City()
input_file_name1 = "node.xls"
input_file_name2 = "link.xls"

# assign citynodes to the city
workbook1 = xlrd.open_workbook(input_file_name1)
worksheet1 = workbook1.sheet_by_name("node")
num_nodes = 686
num_links = 1832
for i in range(num_nodes):
    line_index = i+1
    temp_id = int(worksheet1.cell_value(line_index, 1))
    temp_x = worksheet1.cell_value(line_index, 9)
    temp_y = worksheet1.cell_value(line_index, 10)
    city.add_node(CityNode(temp_id, temp_x, temp_y))

# assign citylinks to the city
workbook2 = xlrd.open_workbook(input_file_name2)
worksheet2 = workbook2.sheet_by_name("link")
for i in range(num_links):
    line_index = i+1
    temp_id = int(worksheet2.cell_value(line_index, 1))
    temp_origin = city.nodes[int(worksheet2.cell_value(line_index, 3))]
    temp_destination = city.nodes[int(worksheet2.cell_value(line_index, 4))]
    
    city.add_link(CityLink(temp_id, temp_origin, temp_destination))
# city.print()
print("read file")
# city.plot_city("rantoul.png")
dj_path, connected = city.dijkstra()
# print(connected)

fleet_size = 50
lmd = 400
T = 1
fleet = Fleet(fleet_size, city, connected)

total_number = 0
total_time = 0
frame_time = 0.0005

events = EventQueue()
temp_passenger_id = 0

# #stable starting point
status_1, status_2 = utils.fleet_status(fleet_size, lmd)
print('Status 1:', status_1)
print('Status 2:', status_2)
#output = Status(idle, assigned, in_service)

status00 = status_1[0]
status01 = status_1[1]
status02 = status_1[2]

# initial conditions
num_vehicle = 0
passengers_plot = {}

while num_vehicle < fleet_size:
    if round(status00) <= num_vehicle < round(status00)+round(status01):
        
        #assigned
        temp_passenger = Passenger(0, temp_passenger_id, city, connected)
        fleet.vehicles[num_vehicle].assign(city, temp_passenger)
        vehicle = fleet.vehicles[num_vehicle]
        passenger = temp_passenger
        px, py = temp_passenger.xy(city)
        passengers_plot[temp_passenger_id] = (px, py)
        print("passenger", temp_passenger_id, "show up")
        
        # t1 is the time of shortest path between vehicle and passenger
        t1 = utils.dist(city, vehicle.node, vehicle.len, passenger.o_node, passenger.o_len) / vehicle.speed
        event1 = Node(t1, 'pick-up', num_vehicle, passenger)

        # t2 is the time of shortest path between passenger origin and destination
        t2 = t1 + utils.dist(city, passenger.o_node, passenger.o_len, passenger.d_node, passenger.d_len) / vehicle.speed
        event2 = Node(t2, 'deliver', num_vehicle, passenger)

        passenger.pick_up = event1
        passenger.deliver = event2
        events.insert(event1)
        events.insert(event2)
        temp_passenger_id += 1

    else:
        if round(status00)+round(status01) <= num_vehicle < fleet_size:
            #in-service
            vehicle = fleet.vehicles[num_vehicle]
            temp_passenger = Passenger(-status01/fleet_size-1/3, temp_passenger_id, city, connected)
            
            while (city.links[vehicle.node.id].destination.id, city.links[temp_passenger.d_node.id].origin.id) not in city.dj_path.keys():
                temp_passenger = Passenger(-status01/fleet_size-1/3, temp_passenger_id, city, connected)
                print("roll again")
                print("error vehicle node")
                print(vehicle.node.id)
            temp_passenger_id += 1
            passenger = temp_passenger

            vehicle.load = 1
            vehicle.passenger = passenger
            vehicle.status = 'in-service'
            
            t1 = utils.dist(city, vehicle.node, vehicle.len, passenger.d_node, passenger.d_len)
            #(current_node, current_len, next_node, next_len, next_trip_length, type, passenger_id)
            current_path = utils.get_path(city, vehicle.node, vehicle.len, passenger.d_node, passenger.d_len)
            vehicle.path += current_path[0]
        
            event1 = Node(t1, 'deliver', num_vehicle, passenger)
            passenger.deliver = event1
            events.insert(event1)
    num_vehicle += 1

print(status00)
print(status01)
print(status02)
output = Status(round(status00), round(status01), fleet_size-round(status00)-round(status01))


# #generate passengers
# t = 0
# while t < T:
#     #move the vehicles
#     dt = random.expovariate(lmd)
#     t += dt
#     #print(t)

#     #generate new passenger
#     temp_passenger = Passenger(t, temp_passenger_id, city, connected)
#     temp_passenger_id += 1

#     #assign passenger
#     event = Node(temp_passenger.t_start, 'appear', None, temp_passenger)
#     events.insert(event)
# print("System initialized ")

# fig_index = 0
# fig_time = 0

# while events.head is not None:
#     event, dt = events.simulate()
#     current_time = event.time

#     while fig_time + frame_time < current_time:
#         print(fig_time)
#         dt = frame_time

#         fig = plt.figure(1)
#         ax = plt.subplot(111)
#         for link in city.links:
#             ax.plot([city.links[link].ox, city.links[link].dx], [city.links[link].oy, city.links[link].dy], "0.8", linewidth = 0.5, zorder = -1)
#         vehicle_idle_x = []
#         vehicle_idle_y = []
#         vehicle_assigned_x = []
#         vehicle_assigned_y = []
#         vehicle_service_x = []
#         vehicle_service_y = []
#         for j in fleet.vehicles:
#             vx, vy = fleet.vehicles[j].xy(city)
#             if fleet.vehicles[j].status == 'idle':
#                 vehicle_idle_x.append(vx)
#                 vehicle_idle_y.append(vy)
#             else:
#                 if fleet.vehicles[j].status == 'assigned':
#                     vehicle_assigned_x.append(vx)
#                     vehicle_assigned_y.append(vy)
#                 else:
#                     vehicle_service_x.append(vx)
#                     vehicle_service_y.append(vy)

#         ax.scatter(vehicle_idle_x, vehicle_idle_y, s = 5, c = "blue", zorder = 1, marker = 'x')
#         ax.scatter(vehicle_assigned_x, vehicle_assigned_y, s = 5, c = "blue", zorder = 1, marker = 'x')
#         ax.scatter(vehicle_service_x, vehicle_service_y, s = 5, c = "black", zorder = 1, marker = 'X')

#         passenger_x = []
#         passenger_y = []
#         for key in passengers_plot.keys():
#             passenger_x.append(passengers_plot[key][0])
#             passenger_y.append(passengers_plot[key][1])

#         ax.scatter(passenger_x, passenger_y, s = 5, c = "red", zorder = 1, marker = 'o')

#         plt.xlim(-88.20, -88.08)
#         plt.ylim(40.27, 40.33)
#         pic_name = 'plot_' + str(fig_index) + '.png'
#         fig.savefig(pic_name)
#         fig.clear()
#         print('figure ', fig_index, 'saved')
#         fig_index += 1

#         fleet.move(dt)
#         events.clock += dt
#         fig_time += dt


#     current_time = fig_time

#     event, dt = events.simulate()
#     current_time = event.time

#     passenger = event.passenger
#     if event.type == 'appear':
#         fleet.move(dt)
#         vehicle_id = fleet.serve(event.passenger)
#         px, py = event.passenger.xy(city)
#         print("passenger", event.passenger.id, "show up")
#         passengers_plot[event.passenger.id] = (px, py)
#         if vehicle_id is None:
#             #print('passenger', passenger.id, 'is not served.')
#             if 0.2*T < current_time:
#                 total_number += 1
#             events.go()
#         else:
#             vehicle = fleet.vehicles[vehicle_id]
#             t1 = current_time + utils.dist(city, vehicle.node, vehicle.len, passenger.o_node, passenger.o_len)
#             event1 = Node(t1, 'pick-up', vehicle_id, passenger)
#             t2 = t1 + utils.dist(city, passenger.o_node, passenger.o_len, passenger.d_node, passenger.d_len)
#             event2 = Node(t2, 'deliver', vehicle_id, passenger)
#             passenger.pick_up = event1
#             passenger.deliver = event2
#             events.insert(event1)
#             events.insert(event2)
#             events.go()
#             output.assign(current_time, vehicle_id, passenger.id, passenger.o_node, passenger.o_len, vehicle.node, vehicle.len)
#     else:
#         vehicle_id = event.vehicle
#         if event.type == 'pick-up':
#             fleet.move(dt)
#             fleet.vehicles[vehicle_id].status = 'in-service'
#             events.go()
#             del passengers_plot[event.passenger.id]
#             print("passenger", event.passenger.id, "deleted")
#             output.pick_up(current_time, vehicle_id, passenger.id, passenger.o_node, passenger.o_len, passenger.o_node, passenger.o_len)
#         else: #event.type == 'deliver'
#             fleet.move(dt)
#             fleet.vehicles[vehicle_id].deliver()
#             events.go()
#             trip_time = current_time - passenger.t_start
#             if 0.2*T < current_time:
#                 total_number += 1
#                 total_time += trip_time
#             output.deliver(current_time, trip_time, vehicle_id, passenger.id, passenger.d_node, passenger.d_len, passenger.d_node, passenger.d_len)



