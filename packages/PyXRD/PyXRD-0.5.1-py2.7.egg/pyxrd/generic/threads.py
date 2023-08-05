# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Author: Mathijs Dumon
# Based on code from Rick Spencer
# Copyright (c) 2013, Mathijs Dumon, Rick Spencer
# All rights reserved.
# Complete license can be found in the LICENSE file.

from traceback import format_exc

import time
from threading import Thread, Event

class CancellableThread(Thread):
    """
        Class for use by ThreadedTaskBox.
    """
    def __init__(self, run_function, on_complete, params=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.run_function = run_function
        self.params = params
        self.on_complete = on_complete
        # Shared flag, passed on to the run_function as 'stop' keyword
        self.__stop = Event()
        # Internal flag, for checking wether the user cancelled or stopped.
        self.__cancel = Event()

    def run(self):
        try:
            # Set up params and include the stop event
            if self.params == None:
                self.params = {}
            self.params["stop"] = self.__stop
            # Tell the function to run
            data = self.run_function(**self.params)
            # Return function results, if not cancelled
            if not self.__cancel.is_set():
                self.on_complete(data)
        except KeyboardInterrupt:
            self.cancel()
        except:
            print "Unhandled exception in CancellableThread run():"
            print format_exc()

    def stop(self):
        """
            Stops the thread, and calls the on_complete callback
        """
        self.__stop.set()
        
    def cancel(self):
        """
            Stops the thread, and does not call the on_complete callback.
        """
        self.__cancel.set()
        self.__stop.set()
        

    pass #end of class
