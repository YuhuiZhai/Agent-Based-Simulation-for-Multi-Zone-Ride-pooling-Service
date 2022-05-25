import numpy as np
def sign(num):
    return (num > 0) - (num < 0)

obj_table = 4000 * np.ones((2, 3))
print(sum(obj_table[0]))