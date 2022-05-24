import random

from pkg_resources import yield_lines 
def sign(num):
    return (num > 0) - (num < 0)

x, y = 0, 0
dx, dy = -3, -3
while (x != dx or y != dy):
    xmove = random.randint(0, 1)
    ymove = 1 - xmove
    if (x == dx):
        xmove, ymove = 0, 1
    elif (y == dy):
        xmove, ymove = 1, 0
    xdir = sign(dx-x)
    ydir = sign(dy-y)
    x += xdir * xmove* 0.5
    y += ydir * ymove* 0.5
    x = xdir*min(xdir*x, xdir*dx) if xdir != 0 else x
    y = ydir*min(ydir*y, ydir*dy) if ydir != 0 else y
    print(x, y)

