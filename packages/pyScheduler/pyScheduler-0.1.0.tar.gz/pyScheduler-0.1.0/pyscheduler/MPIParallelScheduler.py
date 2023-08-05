'''
Created on 16/05/2012

@author: victor
'''
from mpi4py import MPI
from pyscheduler.serialScheduler import SerialScheduler

class MPIParallelScheduler(SerialScheduler):
    """
    Implements an MPI version of the scheduler (powered by mpi4py). It is a gain a master-slave pattern
    implementation, so one process is used to control the protocol.
    """

    def __init__(self, share_results_with_all_processes = False, functions = {}):
        """
        Creates an instance of this scheduler.
        @param share_results_with_all_processes: If true, it will broadcast the final results
        array so that all the processes have a copy of it.
        @param functions: @see SerialScheduler
        """
        SerialScheduler.__init__(self,functions)
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.share_results_with_all_processes = share_results_with_all_processes
        self.number_of_processes = self.comm.Get_size()
        self.running = []


    def run(self):
        """
        Tries to run all the tasks, checking for dependencies. In this case it uses an MPI scheme to handle
        the processes.
        The message protocol is the same as the one used in the ProcessParallelScheduler class.
        """
        self.function_exec('scheduling_started', {"number_of_tasks":len(self.not_completed)})
        # Check that dependencies are OK

        # Wait till all processes are available (the scheduling usually happens in an already set up MPI
        # environment, so we have to ensure that everything syncs before).
        self.comm.Barrier()

        # Execute all tasks
        # rank 0 is the controller

        busy_processes = [False]*(self.number_of_processes)
        busy_processes[0] = True

        available_workers = self.number_of_processes - 1
        while not len(self.finished) == len(self.tasks):
            #
            # 'MASTER' PROCESS
            #
            if self.rank == 0:
                # controller
                cannot_choose_a_task = False
                #Choose an available task
                task_name = self.choose_runnable_task()
                if task_name is not None:
                    # If we can still execute a task we do it (dependency-free task)
                    # but first we need to have an available process
                    available_process = None
                    try:
                        available_process = busy_processes.index(False)
                    except:
                        pass
                    if available_process is not None:
                        self.function_exec('task_started', {"task_name":task_name})
                        self.comm.send(("EXECUTE",task_name), dest = available_process, tag=1)
                        self.lock_task(task_name) # from now on this task is not available for choosing
                        self.running.append(task_name)
                        busy_processes[available_process] = True
                else:
                    cannot_choose_a_task = True

                if cannot_choose_a_task or len(self.running) == available_workers:
                    # Wait for a result
                    ended_task_name, result, sender_rank = self.comm.recv(source = MPI.ANY_SOURCE, tag = 2)
                    self.function_exec('task_ended', {"task_name":ended_task_name, "finished":len(self.finished)})
                    self.results.append(result)
                    self.running.remove(ended_task_name)
                    self.complete_task(ended_task_name)
                    self.remove_from_dependencies(ended_task_name)
                    busy_processes[sender_rank] = False
            #
            # 'SLAVE' PROCESS
            #
            else:
                # Task executing.
                # Wait for a task number to be executed
                message, task_name = self.comm.recv(source = 0, tag = 1)
                if message == "EXECUTE":
                    # Execute it
                    result = self.tasks[task_name].run()
                    # Tell controller that we have finished by sending the result
                    self.comm.send((task_name,result, self.rank), dest = 0, tag = 2)
                elif message == "FINISH":
                    break # exit the loop

        if self.rank == 0:
            for i in range(1,self.number_of_processes):
                self.comm.send(("FINISH",None), dest = i, tag=1)

        if self.share_results_with_all_processes:
            self.results = self.comm.bcast(self.results, root=0)

        self.function_exec('scheduling_ended')

        return self.results


