a = set()
a.add("a")
a.add("a")
a.add("a")
b = 1
for i in a:
    print(i)
    a.remove("a")