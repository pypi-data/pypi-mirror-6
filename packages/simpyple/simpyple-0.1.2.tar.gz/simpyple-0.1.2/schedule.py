class Line(object):
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.slope = float(self.y1 - self.y0) / (self.x1 - self.x0)
        self.displacement = self.y0 - self.slope * self.x0
        
    def value(self, x):     
        return self.slope * x + self.displacement


class Schedule(object):
    def __init__(self, ramp_quantity, full_load_quantity, initial_delay, full_load_delay):
        self.ramp_quantity = ramp_quantity
        self.full_load_quantity = full_load_quantity
        self.initial_delay = initial_delay
        self.full_load_delay = full_load_delay
        self.quantity_profile = 2 * ramp_quantity + full_load_quantity
        self.time = 0

    def next(self, index):
        if index in range(self.ramp_quantity):
            delay = Line(0, self.initial_delay, self.ramp_quantity, self.full_load_delay).value(index)
            self.ramp_up = self.time + delay
        elif index in range(self.ramp_quantity, self.ramp_quantity + self.full_load_quantity):
            delay = self.full_load_delay
            self.full_load = self.time + delay
        elif index in range(self.ramp_quantity + self.full_load_quantity, self.quantity_profile):
            displacement = float(self.initial_delay - self.full_load_delay) / self.ramp_quantity
            delay = displacement + Line(
                self.ramp_quantity + self.full_load_quantity, 
                self.full_load_delay, 
                self.quantity_profile, 
                self.initial_delay
            ).value(index)
            self.ramp_down = self.time + delay
        else:
            delay = self.initial_delay
        self.time += delay
        return self.time
    
    def __str__(self):
        return "Schedule({}, {}, {}, {}), ramp_up={}, full_load={}, ramp_down={}, time={}".format(
            self.ramp_quantity, 
            self.full_load_quantity, 
            self.initial_delay, 
            self.full_load_delay, 
            self.ramp_up, 
            self.full_load, 
            self.ramp_down, 
            self.time
        )
