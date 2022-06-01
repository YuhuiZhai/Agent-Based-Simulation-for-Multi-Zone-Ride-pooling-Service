# import pulp


# inf = 100
# Warehouses = ["1", "2", "4"]
# supply = {"1": 10, "2":30, "4": 10}
# Bars = ["2", "3"]
# demand = {"2": 30, "3": 20}

# # Creates a list of costs of each transportation path
# costs = [
#     [1/100*1/30, 1/100*1/50],
#     [1/80*1/30, 1/80*1/50],
#     [0, 0]
# ]
# costs = pulp.makeDict([Warehouses, Bars], costs, 0)
# prob = pulp.LpProblem("test", pulp.LpMinimize)
# Routes = [(w, b) for w in Warehouses for b in Bars]
# vars = pulp.LpVariable.dicts("Route", (Warehouses, Bars), 0, None, pulp.LpInteger)
# prob += pulp.lpSum([vars[w][b] * costs[w][b] for (w, b) in Routes])

# for w in Warehouses:
#     prob += pulp.lpSum([vars[w][b] for b in Bars]) <= supply[w]

# for b in Bars:
#     prob += pulp.lpSum([vars[w][b] for w in Warehouses]) >= demand[b]
# prob.solve(pulp.PULP_CBC_CMD(msg=0))
# # for v in prob.variables():
# #     print(v.name, "=", v.varValue)
a = "12,3,4"
print(a.split())