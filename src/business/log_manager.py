from typing import TextIO
import queue
from queue import Queue
import sys
from model import Config

#log manager with a thread-save queue for GUI
class LogManager:
    def __init__(self,config:Config):
        self.config=config
        self.log_queue:Queue[str] = queue.Queue()
        
    def configure(self):
        sys.stdout = open(self.config.log_file, 'a')
        sys.stderr = sys.stdout
        # Redirect logs to GUI
        sys.stdout = self.LogProducer(sys.stdout, self.log_queue)
        sys.stderr = self.LogProducer(sys.stderr, self.log_queue)
        
    class LogProducer:
        MAX_QUEUE_SIZE = 1000  # prevent memory explosion
        def __init__(self, original_stream:TextIO, log_queue:Queue[str]):
            self.original_stream = original_stream
            self.log_queue = log_queue
            
        def write(self, message:str):
            self.original_stream.write(message)
            if message.strip():
                if self.log_queue.qsize() < self.MAX_QUEUE_SIZE:
                    self.log_queue.put(message.strip())
                else:
                    pass
        def flush(self):
            pass
