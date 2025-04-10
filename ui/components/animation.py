import time

class Animation:
    """Animation class for smooth transitions"""
    def __init__(self, duration=1.0):
        self.duration = duration
        self.start_time = None
        self.progress = 0
        self.running = False
    
    def start(self):
        self.start_time = time.time()
        self.running = True
        self.progress = 0
    
    def update(self):
        if not self.running:
            return 1
        
        elapsed = time.time() - self.start_time
        self.progress = min(elapsed / self.duration, 1)
        
        if self.progress >= 1:
            self.running = False
        
        return self.progress