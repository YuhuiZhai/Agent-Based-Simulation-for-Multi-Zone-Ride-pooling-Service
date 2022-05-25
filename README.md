# TaxiTransitSimulation

## How to run the simulation. 

1. To run the simulation, go to main.py. The first step is to load the data and create a City object. There are three types of city: `Euclidean`, `Manhattan`, and `real-world`. 

    To create a city with type of `Euclidean` or `Manhattan`, one can create a city with type_name parameter of "Euclidean" or "Manhattan":

        city1 = City(type_name="Euclidean")
        city2 = City(type_name="Manhattan")

    Or one can just create a default City object and input in terminal. 
        
        city = City()

    In the terminal, message will pop out if the city has no type assigned: 

        Please enter the type of city? 
        [1: Euclidean, 2:Manhattan, 3:real-world] 

    Enter the type index (1 or 2 or 3), and then it is finished.

    To create a `real-world` city, here is a simple example of loading graph: 

        # input city information
        city = City("real-world")
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
            temp_destination =\
            city.nodes[int(worksheet2.cell_value(line_index, 4))]
            city.add_link(CityLink(temp_id, temp_origin, temp_destination))
    
2. The next step is to create a Simulation object. To create a Simulation object, the city created before, wanted fleet size, duration of simulation T, and lambda for exponential distribution are needed.

        simulation1 = Simulation(city, fleet_size=50, T=3, lmd=400)

    Simulation object has three types of function for simulating taxi behavior, which are `simple_serve(res)`, `batch_serve(res, dt)`, `sharing_serve(res, detour_percentage)`. 

    Function `simple_serve(res)` is based on time priority, and taxi will respond the passenger immediately. res is the resolution of simulation, and the default value is 1/60/60 (1 sec). To run simple assignment (1 sec resolution), do

        simulation1.simple_serve(res=1/60/60)

    Function `batch_serve(res, dt)` is based on time priority, and taxi will first wait for a while and then respond to the passenger. res is the resolution of simulation, and dt is the batch time gap. To run batch assignment (1 sec resolution and 1 min batch time gap), do:

        simulation1.batch_serve(res=1/60/60, dt=1/60)

    Function `sharing_serve(res, detour_percentage)` is based on time priority, and taxi will allow detour to pick up more than one passengers. res is the resolution of simulation. detour_percentage is the maximum amount of detour percentage allowed. To run rider sharing (1 sec resolution and 60% maximum detour percentage), run the following:  

        simulation1.sharing_serve(res=1/60/60, detour_percentage=0.6)

3. To export the data simulated, use the function of `export()` in Simulation class. There are two datasets produced: `veh_num.csv`, which contains na, ns, ni and passenger number; `fleet_info.csv`, which contains ta, ts, ti, and dist_s (expected service distance).
Example of export a simulation:

        simulation1.export()

4. To create a simulation animation, currently, there is only simple_serve type. Run the function `make_animation(compression, fps)`. compression is the scale of how much the original simulation compressed. fps defines how smooth the animation is. It is not suggested to input a small compression scale. To produce an animation 15 times compressed and with 15 fps, run the following: 

        simulation1.make_animation(compression=15, fps=15)
