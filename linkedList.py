class LinkedList:
    def __init__(self):
        # head and tail node of linked list
        self.head = None
        self.tail = None
        # size of the linked list
        self.clock = 0
        self.size = 0
    
    # print out the list 
    def print_list(self):
        s = "list:"
        if (self.head is not None):
            curr_node = self.head
            while curr_node is not None:
                s = s + " " + str(curr_node.time)
                curr_node = curr_node.next
            print(s)    
        else:
            print("list: empty")
            
        
    # modified
    # insert one node to the linked list
    # the linked list is sorted by ascending time 
    def insert(self, new_node):
        self.size += 1
        temp_node = self.head
        if temp_node is None:
            self.head = new_node
            self.tail = new_node
        else:
            if self.head == self.tail:
                if temp_node.time < new_node.time:
                    temp_node.next = new_node
                    new_node.last = temp_node
                    self.tail = new_node
                else:
                    new_node.next = temp_node
                    temp_node.last = new_node
                    self.head = new_node

            else:
                if self.head.time >= new_node.time:
                    new_node.next = self.head
                    self.head.last = new_node
                    self.head = new_node
                    return
                    
                if self.tail.time < new_node.time:
                    self.tail.next = new_node
                    new_node.last = self.tail
                    self.tail = new_node
                    return

                while temp_node.next is not None:
                    next_node = temp_node.next
                    if temp_node.time < new_node.time <= next_node.time:
                        temp_node.next = new_node
                        new_node.next = next_node
                        next_node.last = new_node
                        new_node.last = temp_node
                        return
                    else:
                        temp_node = next_node

    def simulate(self):
        if self.head is None:
            return None, -1
        else:
            # dt is the time gap between head and starting time
            dt = self.head.time - self.clock

            return self.head, dt
    # time 
    def go(self):
        if self.head is None:
            print('finished')
        else:
            if self.head.vehicle is not None:
                pass
                #print('%f' % event.time, 'vehicle', event.vehicle, event.type, 'passenger', event.passenger.id)
            else:
                pass
                #print('%f' % event.time, 'passenger', event.passenger.id, event.type)
            self.clock = self.head.time
            self.head = self.head.next

    def delete_event(self, event):
        # delete a node in the list
        if self.head == None:
            return 
        if (self.size == 1):
            self.head = None
            self.tail = None
            self.size -= 1
            return 

        if event == self.head:
            self.head = self.head.next
            self.head.prev = None
        elif event == self.tail:
            self.tail = self.tail.last
            self.tail.next = None
        else:   
            last_node = event.last
            next_node = event.next
            last_node.next = next_node
            next_node.last = last_node
        self.size -= 1






