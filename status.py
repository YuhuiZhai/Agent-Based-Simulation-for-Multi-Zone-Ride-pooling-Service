class Status:
    def __init__(self, idle, assigned, in_service):
        self.memory = []
        self.idle = idle
        self.assigned = assigned
        self.in_service = in_service
        self.time = 0
        self.travel_time = 0
        #simultion time/ idle / assigned / in service / event type / passenger x / passenger y / vehicle x / vehicle y / vehicle id / passenger id / total travel time
        self.memory.append((self.time, self.idle, self.assigned, self.in_service, "start", -1, -1, -1, -1, -1, -1, self.travel_time))

    def assign(self, t0, vid, pid, px, py, vx, vy):
        self.assigned += 1
        self.idle -= 1
        self.memory.append((t0, self.idle, self.assigned, self.in_service, 'assign', px, py, vx, vy, vid, pid, 0))

    def deliver(self, t0, t1, vid, pid, px, py, vx, vy):
        self.in_service -= 1
        self.idle += 1
        self.memory.append((t0, self.idle, self.assigned, self.in_service, 'deliver', px, py, vx, vy, vid, pid, t1))

    def pick_up(self, t0, vid, pid, px, py, vx, vy):
        self.in_service += 1
        self.assigned -= 1
        self.memory.append((t0, self.idle, self.assigned, self.in_service, 'pick up', px, py, vx, vy, vid, pid, 0))

    def swap(self, t0, vid0, vid1, pid, px, py, vx0, vy0, vx1, vy1, t_saved):
        self.memory.append((t0, self.idle, self.assigned, self.in_service, 'swap', px, py, vx0, vy0, vid0, pid, 0, t_saved, vx1, vy1, vid1))
