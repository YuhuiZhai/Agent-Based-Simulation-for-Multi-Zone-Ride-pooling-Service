from multiprocessing import Pool, Lock
from itertools import product
import random
from taxi_simul.simulation import Simulation
from city import City
import xlsxwriter as xw
import time 
import numpy as np

start = time.time()
lock = Lock()

def func(info: tuple):
    fs, bg, idx = info
    city = City(type_name="Manhattan")
    s = Simulation(city, fleet_size=fs, T=10, lmd=10000, lr=False, swap=False)
    prob = s.batch_serve(res=5/3600, dt=bg/3600)
    avg_m = sum([prob[i][0] for i in range(len(prob))])/len(prob)
    avg_mpax = sum([prob[i][1] for i in range(len(prob))])/len(prob)
    avg_mveh = sum([prob[i][2] for i in range(len(prob))])/len(prob)
    (t1, t2, t3) = s.passenger_data()[1]
    (at1, at2, at3) = s.passenger_data()[3]
    (ta, avgta) = s.fleet_data()
    
    # do not change
    lock.acquire()
    print(f"count: {idx}, time: {time.time()-start}")
    lock.release()

    return (at1, t1, avgta, avg_m, avg_mpax, avg_mveh)

if __name__ == "__main__":
    with Pool(processes=12) as pool:   
        start = time.time()
        # fleet_size = 44
        # batch_gap = 3

        # fs_g = range(int(5/6*fleet_size), int(7/6*fleet_size))
        fs_g = [1500]
        bg_g = np.arange(5, 240, 5)
        
        result = pool.map(func, [(fs, bg, i) for i, (fs, bg) in enumerate(product(fs_g, bg_g))])
        pool.close()

        workbook = xw.Workbook(f"batch_M{fs_g[0]}_{fs_g[-1]}lmd10000_dt{bg_g[0]}_{bg_g[-1]}.xlsx")
        for i in range(len(fs_g)):
            worksheet1 = workbook.add_worksheet(f"M{fs_g[i]}")
            worksheet1.write(0, 0, "batch gap")
            worksheet1.write(0, 1, "w_pax_a")
            worksheet1.write(0, 2, "w_pax_total")
            worksheet1.write(0, 3, "w_veh")
            worksheet1.write(0, 4, "avg_m")
            worksheet1.write(0, 5, "avg_mpax")
            worksheet1.write(0, 6, "avg_mveh")
            for k in range(len(bg_g)):
                worksheet1.write(k+1, 0, bg_g[k])
                worksheet1.write(k+1, 1, result[i*len(bg_g)+k][0])
                worksheet1.write(k+1, 2, result[i*len(bg_g)+k][1])
                worksheet1.write(k+1, 3, result[i*len(bg_g)+k][2])
                worksheet1.write(k+1, 4, result[i*len(bg_g)+k][3])
                worksheet1.write(k+1, 5, result[i*len(bg_g)+k][4])
                worksheet1.write(k+1, 6, result[i*len(bg_g)+k][5])
        workbook.close()
        print(time.time() - start)