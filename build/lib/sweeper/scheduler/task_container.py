__author__ = '@dominofire'


import logging
import threading
from paramiko import SSHException
import sweeper.utils as utils
import os


class TaskContainer(threading.Thread):
    """
    A class that stores info for executing a task
    in a cloud resource
    """
    def __init__(self, task, vm, start_time_expected):
        threading.Thread.__init__(self)
        self.task = task
        self.vm = vm
        self.start_time_expected = start_time_expected
        self.status_lock = threading.Lock()
        self._status = -1  # not started

    @property
    def status(self):
        #self.status_lock.acquire()
        st = self._status
        #self.status_lock.release()
        return st

    @status.setter
    def status(self, st):
        self.status_lock.acquire()
        self._status = st
        self.status_lock.release()

    def __repr__(self):
        return 'TaskContainer({},{},{})'.format(self.task.name, self.vm.name, self._status)

    # Override
    def run(self):
        try:
            self.status = 0  # running
            logging.debug('Executing Task {}'.format(self.task))
            # TODO: Remove hardcored path
            p_stdin, p_stdout, p_stderr, client = self.vm.execute_command(self.task.command, working_dir='/opt/fileshare')
            logging.debug('Executing Task {} complete'.format(self.task))

            out = open('{}.stdout'.format(self.task.name), 'wb')
            err = open('{}.stderr'.format(self.task.name), 'wb')

            block_size = 4096
            buffer_out = bytearray(p_stdout.read(block_size))
            buffer_err = bytearray(p_stderr.read(block_size))
            #non blocking
            while len(buffer_out) > 0 or len(buffer_err) > 0:
                if len(buffer_out) > 0:
                    # TIP: Don't assume encoding
                    out.write(buffer_out)  # TODO: it would be nicer if we use resource's encoding
                    buffer_out = bytearray(p_stdout.read(block_size))
                if len(buffer_err) > 0:
                    err.write(buffer_err)  # TODO: it would be nicer if we use resource's encoding
                    buffer_err = bytearray(p_stderr.read(block_size))
            out.close()
            err.close()

            logging.debug('Disconnecting to resource {}'.format(self.vm.name))
            client.close()
            logging.debug('Disconnecting to resource {} complete'.format(self.vm.name))

            logging.debug('Task {} executed successfully on resource {}'.format(self.task, self.vm.name))

            logging.info('Downloading required files...')
            for fp in self.task.download_files:
                base, file, ext = utils.split_path(fp)
                logging.info('Downloading file {}'.format(fp))
                #  TODO: remove location hardcoded
                self.vm.get_file('/opt/fileshare/{}'.format(fp), utils.join_path(os.getcwd(), file, ext))
                logging.info('Downloading file {} complete'.format(fp))
            logging.info('Downloading required files complete')

            self.status = 1  # completed
        except SSHException as ex:
            self.status = 2  # error
            logging.error('Error executing task:{}'.format(ex.message))
        except Exception as ex2:
            self.status = 2  # error
            logging.error('Error executing task:{}'.format(ex2.message))
