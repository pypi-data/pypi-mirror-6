""" Module for interaction between ncs-daemon and the ncs simulator """
import ncs
import os
from ncsdaemon.crypt import Crypt
from datetime import datetime
import json
from threading import Thread
from ncsdaemon.util import WriteRedirect

SIM_DATA_DIRECTORY = '/var/ncs/sims/'

class SimThread(Thread):
    """ Thread that contains the running simulation """

    helper = None
    sim = None
    step = None

    def __init__(self, helper, sim, step):
        # call the superstructor for the Thread class, otherwise demons emerge
        super(SimThread, self).__init__()
        self.sim = sim
        self.step = step
        self.helper = helper

    def run(self):
        # Run the simulation
        self.sim.step(self.step)
        # Once it's done, change the helper's status
        self.helper.is_running = False


class SimHelperBase(object):
    """ Abstract base for the sim object """

    def get_status(self):
        """ Gets the status of the simulator """
        pass

    def run(self, user, model):
        """ Tells the simulator to run with the current configureation """
        pass

    def stop(self):
        """ Tells the simulator to stop """
        pass

class SimHelper(SimHelperBase):
    """ This class handles interaction with the NCS simulator """

    _instance = None
    sim_status = None
    is_running = False
    simulation = None
    most_recent_sim_info = None

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(SimHelper, self).__new__(
                                self, *args, **kwargs)
        return self._instance

    def __init__(self):
        if not os.path.exists(SIM_DATA_DIRECTORY):
            os.makedirs(SIM_DATA_DIRECTORY)

    def get_status(self):
        """ Get the status of the simulation """
        # if the sim is running, send info about the currently running sim
        if self.is_running:
            return self.most_recent_sim_info
        # otherwise say its idle
        else:
            info = {
                "status": "idle"
            }
            return info

    def run(self, user, model):
        """ Runs a simulation """
        self.simulation = ncs.Simulation()
        if not self.simulation.init([]):
            info = {
                "status": "error",
                "message": "Failed to initialize simulation"
            }
            return info
        # generate a new ID for the ism
        sim_id = Crypt.generate_sim_id()
        #create the directory for sim information like reports
        os.makedirs(SIM_DATA_DIRECTORY + '/' + sim_id)
        # get a timestamp
        now = datetime.now()
        # get a formatted string of the timestamp
        time_string = now.strftime("%d/%m/%Y %I:%M:%S %p %Z")
        # info object to be sent back to the user
        info = {
            "status": "running",
            "user": user,
            "started": time_string,
            "sim_id": sim_id
        }
        # meta object for the sim directory
        meta = {
            "user": user,
            "started": time_string,
            "sim_id": sim_id
        }
        # write the status info to the directory
        with open(SIM_DATA_DIRECTORY + '/' + sim_id + '/meta.json', 'w') as fil:
            fil.write(json.dumps(meta))
        # store the info as the most recent sim info
        self.most_recent_sim_info = info
        # create a new thread for the simulation
        sim_thread = SimThread(self, self.simulation, 5)
        # start running the simulation
        sim_thread.start()
        # set the sim to running
        self.is_running = True
        return info

    def stop(self):
        """ Stop the simulation """
        # if there was a simulation running, shut it down
        if self.simulation.shutdown():
            # set current status to stopped
            self.sim_status['status'] = 'idle'
            return self.sim_status
        # otherwise indicate that
        else:
            info = {
                "status": "error",
                "message": "No simulation was running"
            }
            return info

