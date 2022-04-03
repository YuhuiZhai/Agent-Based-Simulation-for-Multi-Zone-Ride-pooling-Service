# from linkedList import LinkedList
# from node import Node
# l = LinkedList()
# n1 = Node(2,1,1,1)
# n2 = Node(2,1,1,1)
# n3 = Node(3,1,1,1)
# n4 = Node(4,1,1,1)

# l.insert(n1)
# l.insert(n3)
# l.insert(n4)
# l.insert(n2)
# l.print_list()
# l.delete_event(n1)
# l.delete_event(n2)
# l.delete_event(n3)
# l.delete_event(n4)
# l.print_list()
import matplotlib.pyplot as plt
import heapq as hq
queue = []
a = [1,2,3,4]
b = [2,3,4]
queue += a
queue += b
print(queue)