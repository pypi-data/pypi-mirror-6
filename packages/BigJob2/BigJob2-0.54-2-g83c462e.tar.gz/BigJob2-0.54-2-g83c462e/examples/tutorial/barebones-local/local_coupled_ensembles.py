import os
import sys
import saga
import pilot
import traceback

""" This tutorial example shows another form of task set synchronization.
    It exemplifies a simple  workflow which submit a set of tasks (set A) and
    (set B) and wait until they are completed until it submits another set of
    tasks (set C). Both A- and B-tasks are 'producers'. C-tasks 'consumers' and
    concatenate the output of an A- and a B-tasks.
"""

#------------------------------------------------------------------------------
# Redis password and 'user' name
REDIS_PWD   = # Fill in the password to your server
USER_NAME   = # Fill in your username on the resource you're running on

# The coordination server
COORD       = "redis://%s@localhost:6379" % REDIS_PWD
# The host to run BigJob on
HOSTNAME    = "localhost"
# The working directory on your machine
WORKDIR     = "/home/%s/example1" % USER_NAME
# The number of jobs you want to run
NUMBER_JOBS = 4


#------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:
        # this describes the parameters and requirements for our pilot job
        pilot_description = pilot.PilotComputeDescription()
        pilot_description.service_url = "fork://%s" % HOSTNAME
        pilot_description.number_of_processes = NUMBER_JOBS
        pilot_description.working_directory = WORKDIR
        pilot_description.walltime = 10

        # create a new pilot job
        pilot_compute_service = pilot.PilotComputeService(COORD)
        pilotjob = pilot_compute_service.create_pilot(pilot_description)

        # submit 'A' tasks to pilot job
        task_set_A = list()
        for i in range(NUMBER_JOBS):
            task_desc = pilot.ComputeUnitDescription()
            task_desc.executable = '/bin/echo'
            task_desc.arguments = ['I am an $TASK_SET task with id $TASK_NO', ]
            task_desc.environment = {'TASK_SET': 'A', 'TASK_NO': i}
            task_desc.number_of_processes = 1
            task_desc.output = 'A-stdout.txt'
            task_desc.error  = 'A-stderr.txt'
            task = pilotjob.submit_compute_unit(task_desc)
            print "* Submitted 'A' task '%s' with id '%s'" % (i, task.get_id())
            task_set_A.append(task)

        # submit 'B' tasks to pilot job
        task_set_B = list()
        for i in range(NUMBER_JOBS):
            task_desc = pilot.ComputeUnitDescription()
            task_desc.executable = '/bin/echo'
            task_desc.arguments = ['I am a $TASK_SET task with id $TASK_NO']
            task_desc.environment = {'TASK_SET': 'B', 'TASK_NO': i}
            task_desc.number_of_processes = 1
            task_desc.output = 'B-stdout.txt'
            task_desc.error  = 'B-stderr.txt'
            task = pilotjob.submit_compute_unit(task_desc)
            print "* Submitted 'B' task '%s' with id '%s'" % (i, task.get_id())
            task_set_B.append(task)

        # ---------------------------------------------------------------------
        print "Waiting for 'A' and 'B' tasks to complete..."
        pilotjob.wait()
	print "Executing 'C' tasks now…"
        # ---------------------------------------------------------------------

        # submit 'C' tasks to pilot job. each 'C' task takes the output of
        # an 'A' and a 'B' task and puts them together.
        task_set_C = list()
        for i in range(NUMBER_JOBS):
            task_desc = pilot.ComputeUnitDescription()
            task_desc.executable = '/bin/echo'
            task_desc.arguments = ['I am a $TASK_SET task with id $TASK_NO']
            task_desc.environment = {'TASK_SET': 'C', 'TASK_NO': i}
            task_desc.number_of_processes = 1
            task_desc.output = 'C-stdout.txt'
            task_desc.error  = 'C-stderr.txt'
            task = pilotjob.submit_compute_unit(task_desc)
            print "* Submitted 'C' task '%s' with id '%s'" % (i, task.get_id())
            task_set_C.append(task)

        # ---------------------------------------------------------------------
        print "Waiting for 'C' tasks to complete..."
        pilotjob.wait()
        # ---------------------------------------------------------------------

    except Exception, ex:
            print "AN ERROR OCCURED: %s" % ((str(ex)))
            # print a stack trace in case of an exception -
            # this can be helpful for debugging the problem
            traceback.print_exc()
            sys.exit(-1)

    finally:
        # alway try to shut down pilots, otherwise jobs might end up
        # lingering in the queue
        print ("Terminating BigJob...")
        pilotjob.cancel()
        pilot_compute_service.cancel()


