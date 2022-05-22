# Initialise the graph
table = {"1":"Euclidean", "2":"Mahattan", "3":"real-world", 
        "Euclidean":"Euclidean", "Mahattan":"Mahattan", "real-world":"real-world"}
print("Please enter the type of city? \n [1: Euclidean, 2:Mahattan, 3:real-world]")
print(table.keys())
answer = input()
if answer in table.keys():
    print(table[answer])
else:
    print("Wrong input, please try again")