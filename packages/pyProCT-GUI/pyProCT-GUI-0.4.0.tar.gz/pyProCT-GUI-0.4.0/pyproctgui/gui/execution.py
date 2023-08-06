'''
Created on 08/05/2013

@author: victor
'''
import threading
import traceback
from pyproct.driver.driver import Driver
from pyproctgui.gui.exceptionThread import ThreadWithExc

def set_status(status, action , value = None):
    status["status"] = action
    if value is None:
        status["value"] = False
    else:
        status["value"] = value

class StatusListener(threading.Thread):

    def __init__(self,data_source, status):
        super(StatusListener, self).__init__()
        self._stop = threading.Event()
        self.data_source = data_source
        self.status = status
        self.step ="initializing"

    def stop(self):
        self._stop.set()
        self.data_source.notify("Main","Stop","Finished")

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        """
        Main function of the listener object in the Executor thread (this is actually a separated thread).
        It parses pyProCT notifications and changes the shared status object. Access to shared elements is
        not protected.
        Status object must contain two values:
        "status" -> Description of the current status.
        "value" -> A value associated with the current status (for instance completion value).
        """
        global ongoing_clustering

        scheduler_status = {"message":"","total":0, "done":0}

        while not self.stopped():
            self.data_source.data_change_event.wait()
            data = self.data_source.get_data()

            action = data.contents["action"]
            value = data.contents["message"]

            if action == "Matrix calculation":
                set_status(self.status, "Matrix Calculation ...")
            elif action ==  "Exploration Started":
                self.step ="clustering"
                set_status(self.status, "Generating parameters for exploration ...")
            elif action == "Scheduler Starts":
                if self.step == "clustering":
                    # First is clustering, second is evaluation. This is somewhat hardcoded behaviour... sorry!!
                    scheduler_status["message"] = "Clustering exploration ..."
                    self.step = "evaluation"
                else:
                    scheduler_status["message"] = "Evaluating clusterings ..."
                scheduler_status["total"] = value['number_of_tasks']
                scheduler_status["done"] = 0
                set_status(self.status, scheduler_status["message"], 0)
            elif action == "Task Ended":
                scheduler_status["done"] =  value["finished"]
                set_status(self.status, scheduler_status["message"], scheduler_status["done"])
            elif action == "Filter":
                #Next is to evaluate clusterings
                self.step ="evaluation" # redundancies help when messages are lost
                set_status(self.status, "Filtering generated clusterings ...")

            self.data_source.data_change_event.clear()
            if self.data_source.data.contents["action"] == "SHUTDOWN":
                break
        self.status["status"] = "Ended"
        print "statusListener ended"

class ExecutionThread(ThreadWithExc):
    def __init__(self, observer, parameters):
        super(ExecutionThread, self).__init__()
        self.observer = observer
        self.parameters = parameters
        self.status = {"status":"Initializing...","value":False}
        self.driver = None
        self.driver_process = None

    def run(self):
        global ongoing_clustering
        ongoing_clustering = True
        self.status_listener = StatusListener(self.observer, self.status)
        self.status_listener.start()
        try:
            self.driver = Driver(self.observer)
            self.driver.run(self.parameters)
        except Exception, e:
            print e
            print traceback.format_exc()
        finally:
            self.status_listener.stop()
            self.observer.notify("ExecutionThread","SHUTDOWN","Driver ended.")
            ongoing_clustering = False
            print "Exethread ended"
