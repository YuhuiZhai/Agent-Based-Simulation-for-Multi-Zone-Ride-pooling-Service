import xlrd
import random 
from city import CityNode
from city import CityLink
from city import City
from simulation import Simulation

random.seed(2)
# input city information
city = City()
# input_file_name1 = "node.xls"
# input_file_name2 = "link.xls"

# # assign citynodes to the city
# workbook1 = xlrd.open_workbook(input_file_name1)
# worksheet1 = workbook1.sheet_by_name("node")
# num_nodes = 686
# num_links = 1832
# for i in range(num_nodes):
#     line_index = i+1
#     temp_id = int(worksheet1.cell_value(line_index, 1))
#     temp_x = worksheet1.cell_value(line_index, 9)
#     temp_y = worksheet1.cell_value(line_index, 10)
#     city.add_node(CityNode(temp_id, temp_x, temp_y))

# # assign citylinks to the city
# workbook2 = xlrd.open_workbook(input_file_name2)
# worksheet2 = workbook2.sheet_by_name("link")
# for i in range(num_links):
#     line_index = i+1
#     temp_id = int(worksheet2.cell_value(line_index, 1))
#     temp_origin = city.nodes[int(worksheet2.cell_value(line_index, 3))]
#     temp_destination =\
#     city.nodes[int(worksheet2.cell_value(line_index, 4))]
    
#     city.add_link(CityLink(temp_id, temp_origin, temp_destination))
# print("read file completed")

# simple assignment part
simulation1 = Simulation(city, fleet_size=10, T=3, lmd=50)
# simulation1.simple_serve(res=1/60/60)
# simulation1.export("simple")

# batch assignment part
simulation1.batch_serve(res=1/60/60, dt=1/10)
# simulation1.export("batch")

# share assignment
# simulation1.sharing_serve(res=1/60/60, detour_percentage=5)

# animation part
# simulation1.export("share")
# simulation1.export()
simulation1.make_animation(compression=20, fps=15)

