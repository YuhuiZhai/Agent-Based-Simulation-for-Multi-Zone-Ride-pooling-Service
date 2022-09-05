# TaxiTransitSimulation

## How to run the simulation. 

1. This version is to simulate hetergeneous demand ride-sharing case. Details can be referenced in the paper " ... ".

2. The first step is to create a `City` object. To create a `City` object, input is the `length` (the city length), `n` (to create n x n blocks), and the `prob_matrix` (to store deltaij_dir)

        city = City(length=2, n=2, prob_matrix=prob_m)

    `prob_matrix` has the shape k x k x 4. It has the pattern that: 

        prob_matrix[i][j] = [prob_N, prob_E, prob_W, prob_S]

3. After creating a city, we can now run the simulation by creating a `Simulation ` object. A `Simulation` object needs `city`, `T` (study time duration), `lmd_matrix` (flow matrix form zone i to j), `fleet_matrix` (matrix storing fleet size in each zone), and `rebalance_matrix` (matrix storing rebalance rate bij).

        s = Simulation(city=city, T=5, lmd_matrix=lmd_m, fleet_matrix=fleet_m, rebalance_matrix=rebalance_m)

4. To make the simulation run, call the `simple_serve(res)` function. `res` is the time resolution (unit in hr). 

        # one second simulation
        s.simple_serve(res=1/3600)


4. To export the data simulated, use the function of `export_state_number()` in Simulation class. This will export the number of taxi in each status varying with time.  

        s.export_state_number()

5. To create a simulation animation. Run the function `make_animation(compression, fps)`. compression is the scale of how much the original simulation compressed. fps defines how smooth the animation is. It is not suggested to input a small compression scale. To produce an animation 15 times compressed and with 15 fps, run the following: 

        s.make_animation(compression=15, fps=15)
