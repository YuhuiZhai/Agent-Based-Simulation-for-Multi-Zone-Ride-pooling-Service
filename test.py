import scipy.optimize as sp
M = 10
R = 3.6
L = 2.4
v = 18
lbd = 100
def f(Ta):
    opt_M = 0.63**2*R/(v*Ta**2) + lbd*Ta + lbd*L/v - 100
    return opt_M
def fprime(Ta):
    return -2*0.63**2*R/v**2/Ta**3 + lbd 
opt = (2*0.63**2*R/v**2/lbd)**(1/3)

print(f(10e-10))
print(f(opt))
sol = sp.root_scalar(f, bracket=[10e-10, opt], method='bisect')
print(sol.root)