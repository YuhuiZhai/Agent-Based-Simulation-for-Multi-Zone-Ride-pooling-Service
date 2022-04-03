import heapq as hq
class EventQueue:
    def __init__(self):
        # event queue
        # size of queue
        # current time 
        self.queue = []
        self.size = 0
        self.clock = 0

    # add an event to the queue
    # type of event is class Node
    def insert(self, event):
        self.size += 1
        hq.heappush(self.queue, (event.time, event))

    # pop the event with the minimum time 
    # return the popped time and event
    def dequeue(self):
        self.size -= 1
        time, event = hq.heappop(self.queue)
        self.clock += time
        return time, event
    
    # delete an event in the queue
    # type of event is class Node
    def delete(self, event):
        if ((event.time, event) in self.queue):
            self.queue.remove((event.time, event))
        hq.heapify(self.queue)

    def simulate(self):
        if len(self.queue) == 0:
            return None, -1
        else:
            head_time, head = self.queue[0]
            dt = head_time - self.clock
            return head, dt

    # def go(self):
    #     if len(self.queue) == 0:
    #         print('finished')
    #     else:
    #         head_time, head = self.queue[0]
    #         if head.vehicle is not None:
    #             pass
    #             #print('%f' % event.time, 'vehicle', event.vehicle, event.type, 'passenger', event.passenger.id)
    #         else:
    #             pass
    #             #print('%f' % event.time, 'passenger', event.passenger.id, event.type)
    #         self.clock = head_time
    #         self.head = self.head.next


