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
    fs, bg, lmd, idx, radius = info
    city = City(type_name="Manhattan")
    s = Simulation(city, fleet_size=fs, T=10, lmd=lmd, lr=False, swap=False)
    batch_data, (avg_m, avg_mpax, avg_mveh, avg_pdist) = s.batch_serve(res=5/3600, dt=bg/3600, r=radius)
    
    (tm, ta, ts, t), (avgtm, avgta, avgts, avgt) = s.passenger_data_batch()
    (avg_tm, avg_ta), (avg_na, avg_ns, avg_ni) = s.fleet_data()[0], s.fleet_data()[1]
    
    # do not change
    lock.acquire()
    print(f"count: {idx}, time: {time.time()-start}")
    lock.release()

    return (avg_m, avg_mpax, avg_mveh, avg_pdist, avgtm, avgta, avgt, avg_tm, avg_ta, avg_na, avg_ns, avg_ni)

if __name__ == "__main__":
    with Pool(processes=12) as pool:   
        start = time.time()
        fs_g = [1000, 1200, 1400, 1600]
        bg_g = [10]
        lmd = 7200
        radius = 0.05

        result = pool.map(func, [(fs, bg, lmd, i, radius) for i, (fs, bg) in enumerate(product(fs_g, bg_g))])
        pool.close()

        workbook = xw.Workbook(f"batch_M{fs_g[0]}_{fs_g[-1]}lmd{lmd}_dt{bg_g[0]}_{bg_g[-1]}_r_{radius}.xlsx")
        for i in range(len(fs_g)):
            worksheet1 = workbook.add_worksheet(f"M{fs_g[i]}")
            worksheet1.write(0, 0, "batch gap")
            worksheet1.write(0, 1, "matching number m")
            worksheet1.write(0, 2, "pax matching number md")
            worksheet1.write(0, 3, "veh matching number ms")
            worksheet1.write(0, 4, "pick up distance L")
            worksheet1.write(0, 5, "pax matching time")
            worksheet1.write(0, 6, "pax assigned time")
            worksheet1.write(0, 7, "pax total traveling time")
            worksheet1.write(0, 8, "veh matching time")
            worksheet1.write(0, 9, "veh assigned time")
            worksheet1.write(0, 10, "na")
            worksheet1.write(0, 11, "ns")
            worksheet1.write(0, 12, "ni")
            for k in range(len(bg_g)):
                worksheet1.write(k+1, 0, bg_g[k])
                worksheet1.write(k+1, 1, result[i*len(bg_g)+k][0])
                worksheet1.write(k+1, 2, result[i*len(bg_g)+k][1])
                worksheet1.write(k+1, 3, result[i*len(bg_g)+k][2])
                worksheet1.write(k+1, 4, result[i*len(bg_g)+k][3])
                worksheet1.write(k+1, 5, result[i*len(bg_g)+k][4])
                worksheet1.write(k+1, 6, result[i*len(bg_g)+k][5])
                worksheet1.write(k+1, 7, result[i*len(bg_g)+k][6])
                worksheet1.write(k+1, 8, result[i*len(bg_g)+k][7])
                worksheet1.write(k+1, 9, result[i*len(bg_g)+k][8])
                worksheet1.write(k+1, 10, result[i*len(bg_g)+k][9])
                worksheet1.write(k+1, 11, result[i*len(bg_g)+k][10])
                worksheet1.write(k+1, 12, result[i*len(bg_g)+k][11])
        workbook.close()
        print(time.time() - start)