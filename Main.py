import threading
import time


class CommandThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(CommandThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event() 
        self.__flag.set() 
        self.__running = threading.Event() 
        self.__running.set() 

    def run(self):
        while self.__running.isSet():
            self.__flag.wait() 
            time.sleep(1)

    def pause(self):
        self.__flag.clear() 

    def resume(self):
        self.__flag.set() 

    def stop(self):
        self.__flag.set() 
        self.__running.clear()