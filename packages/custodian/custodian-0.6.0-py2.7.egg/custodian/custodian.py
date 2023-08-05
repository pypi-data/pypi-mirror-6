#!/usr/bin/env python

"""
This module implements the main Custodian class, which manages a list of jobs
given a set of error handlers, the abstract base classes for the
ErrorHandlers and Jobs, and some helper functions for backing up or
compressing files in a directory.
"""

from __future__ import division

__author__ = "Shyue Ping Ong, William Davidson Richards"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "May 3, 2013"

import logging
import subprocess
import datetime
import time
import json
from glob import glob
import tarfile
import os
import tempfile
import shutil
from abc import ABCMeta, abstractmethod, abstractproperty
from gzip import GzipFile

pjoin = os.path.join


class Custodian(object):
    """
    The Custodian class is the manager for a list of jobs given a list of
    error handlers. The way it works is as follows:

    1. Let's say you have defined a list of jobs as [job1, job2, job3, ...] and
       you have defined a list of possible error handlers as [err1, err2, ...]
    2. Custodian will run the jobs in the order of job1, job2, ... During each
       job, custodian will monitor for errors using the handlers that have
       is_monitor == True. If an error is detected, corrective measures are
       taken and the particular job is rerun.
    3. At the end of each individual job, Custodian will run through the list
       error handlers that have is_monitor == False. If an error is detected,
       corrective measures are taken and the particular job is rerun.

    .. attribute: max_errors

        Maximum number of errors allowed.

    .. attribute: handlers

        All error handlers (including monitors). All error handlers are used
        to check for errors at the end of a run.

    .. attribute: monitors

        Error handlers that are Monitors, i.e., handlers that monitors a job
        as it is being run.

    .. attribute: polling_time_step

        The length of time in seconds between steps in which a job is
        checked for completion.

    .. attribute: monitor_freq

        The number of polling steps before monitoring occurs. For example,
        if you have a polling_time_step of 10 seconds and a monitor_freq of
        30, this means that Custodian uses the monitors to check for errors
        every 30 x 10 = 300 seconds, i.e., 5 minutes.
    """
    LOG_FILE = "custodian.json"

    def __init__(self, handlers, jobs, max_errors=1, polling_time_step=10,
                 monitor_freq=30, log_file="custodian.json",
                 skip_over_errors=False, scratch_dir=None,
                 gzipped_output=False, checkpoint=True):
        """
        Args:
            handlers:
                Error handlers. In order of priority of fixing.
            jobs:
                List of Jobs to be run sequentially.
            max_errors:
                Maximum number of errors allowed before exiting.
            polling_time_step:
                The length of time in seconds between steps in which a
                job is checked for completion. Defaults to 10 seconds.
            monitor_freq:
                The number of polling steps before monitoring occurs. For
                example, if you have a polling_time_step of 10seconds and a
                monitor_freq of 30, this means that Custodian uses the
                monitors to check for errors every 30 x 10 = 300 seconds,
                i.e., 5 minutes.
            log_file:
                Deprecated. Custodian now always logs to a custodian.json
                file.
            skip_over_errors:
                If set to True, custodian will skip over error handlers that
                failed (raised an Exception of some sort). Otherwise,
                custodian will simply exit on unrecoverable errors.
                The former will lead to potentially more robust performance,
                but may make it difficult to improve handlers. The latter
                will allow one to catch potentially bad error handler
                implementations. Defaults to False.
            scratch_dir:
                If this is set, any files in the current directory are copied
                to a temporary directory in a scratch space first before any
                jobs are performed. This is useful in some setups where a
                scratch partition has much faster IO. To use this, set
                scratch_dir=root of directory you want to use for runs.
                There is no need to provide unique directory names; we will
                use python's tempfile creation mechanisms. If this is
                None (the default), the run is performed in the current
                working directory.
            gzipped_output:
                Whether to gzip the final output to save space. Defaults to
                False.
            checkpoint:
                Whether to checkpoint after each Job. Defaults to True.
        """
        self.max_errors = max_errors
        self.jobs = jobs
        self.handlers = handlers
        self.monitors = filter(lambda x: x.is_monitor, handlers)
        self.polling_time_step = polling_time_step
        self.monitor_freq = monitor_freq
        self.skip_over_errors = skip_over_errors
        self.scratch_dir = scratch_dir
        self.gzipped_output = gzipped_output
        self.checkpoint = checkpoint

    @staticmethod
    def _load_checkpoint(fname):
        logging.info("Loading from checkpoint file {}...".format(fname))
        t = tarfile.open(fname)
        t.extractall()
        #Log the corrections to a json file.
        with open(Custodian.LOG_FILE, "r") as f:
            run_log = json.load(f)
        return run_log

    @staticmethod
    def _delete_checkpoints(cwd):
        for f in glob(pjoin(cwd, "custodian.chk.*.tar.gz")):
            os.remove(f)

    @staticmethod
    def _save_checkpoint(cwd, index):
        try:
            Custodian._delete_checkpoints(cwd)
            name = shutil.make_archive(
                pjoin(cwd, "custodian.chk.{}".format(index)), "gztar")
            logging.info("Checkpoint written to {}".format(name))
        except Exception as ex:
            logging.info("Checkpointing failed")

    def run(self):
        """
        Runs the job.

        Returns:
            All errors encountered as a list of list.
            [[error_dicts for job 1], [error_dicts for job 2], ....]
        """
        cwd = os.getcwd()

        if self.scratch_dir is not None:
            tempdir = tempfile.mkdtemp(dir=self.scratch_dir)
            for f in os.listdir("."):
                shutil.copy(f, tempdir)
            os.chdir(tempdir)
            logging.info("Using scratch directory {}.".format(tempdir))

        run_log = []
        total_errors = 0
        unrecoverable = False
        start = datetime.datetime.now()
        logging.info("Run started at {}.".format(start))

        for i, job in enumerate(self.jobs):
            chk_fname = pjoin(cwd, "custodian.chk.{}.tar.gz".format(i))
            if self.checkpoint and os.path.exists(chk_fname):
                run_log = Custodian._load_checkpoint(chk_fname)
                continue
            run_log.append({"job": job.to_dict, "corrections": []})
            for attempt in xrange(self.max_errors):
                logging.info(
                    "Starting job no. {} ({}) attempt no. {}. Errors thus far"
                    " = {}.".format(i + 1, job.name, attempt + 1,
                                    total_errors))

                # If this is the start of the job, do the setup.
                if not run_log[-1]["corrections"]:
                    job.setup()

                p = job.run()
                # Check for errors using the error handlers and perform
                # corrections.
                has_error = False

                # While the job is running, we use the handlers that are
                # monitors to monitor the job.
                if isinstance(p, subprocess.Popen):
                    if self.monitors:
                        n = 0
                        while True:
                            n += 1
                            time.sleep(self.polling_time_step)
                            if p.poll() is not None:
                                break
                            if n % self.monitor_freq == 0:
                                corrections = _do_check(
                                    self.monitors, terminate_func=p.terminate,
                                    skip_over_errors=self.skip_over_errors)
                                if len(corrections) > 0:
                                    has_error = True
                                    total_errors += len(corrections)
                                    run_log[-1]["corrections"].extend(
                                        corrections)
                    else:
                        p.wait()

                # Check for errors again, since in some cases non-monitor
                # handlers fix the problems detected by monitors
                # if an error has been found, not all handlers need to run
                if has_error:
                    remaining_handlers = filter(lambda x: not x.is_monitor,
                                                self.handlers)
                else:
                    remaining_handlers = self.handlers

                corrections = _do_check(
                    remaining_handlers,
                    skip_over_errors=self.skip_over_errors)
                if len(corrections) > 0:
                    has_error = True
                    total_errors += len(corrections)
                    run_log[-1]["corrections"].extend(corrections)

                #Log the corrections to a json file.
                with open(Custodian.LOG_FILE, "w") as f:
                    logging.info("Logging to {}...".format(Custodian.LOG_FILE))
                    json.dump(run_log, f, indent=4)

                # If there are no errors detected, perform postprocessing and
                # exit.
                if not has_error:
                    job.postprocess()
                    break
                elif run_log[-1]["corrections"][-1]["actions"] is None:
                    # Check if there has been an unrecoverable error.
                    logging.info("Unrecoverable error.")
                    unrecoverable = True
                    break
                elif total_errors >= self.max_errors:
                    logging.info("Max errors reached.")
                    break

            if unrecoverable or total_errors >= self.max_errors:
                break

            # Checkpoint after each job so that we can recover from last
            # point and remove old checkpoints
            if self.checkpoint:
                Custodian._save_checkpoint(cwd, i)

        end = datetime.datetime.now()
        logging.info("Run ended at {}.".format(end))
        run_time = end - start
        if total_errors >= self.max_errors:
            logging.info("Max {} errors reached. Exited..."
                         .format(self.max_errors))
        elif not unrecoverable:
            #Cleanup checkpoint files (if any) if run is successful.
            Custodian._delete_checkpoints(cwd)

        logging.info("Run completed. Total time taken = {}.".format(run_time))

        if self.gzipped_output:
            gzip_dir(".")

        if self.scratch_dir is not None:
            for f in os.listdir("."):
                shutil.copy(f, cwd)
            shutil.rmtree(tempdir)
            os.chdir(cwd)

        return run_log


def _do_check(handlers, terminate_func=None, skip_over_errors=False):
    corrections = []
    for h in handlers:
        try:
            if h.check():
                if terminate_func is not None and h.is_terminating:
                    terminate_func()
                d = h.correct()
                logging.error(str(d))
                corrections.append(d)
        except Exception as ex:
            if not skip_over_errors:
                raise
            else:
                corrections.append(
                    {"errors": ["Bad handler " + str(h)],
                     "actions": []})
    return corrections


class ErrorHandler(object):
    """
    Abstract base class defining the interface for an ErrorHandler.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self):
        """
        This method is called at the end of a job. Returns a boolean value
        indicating if errors are detected.
        """
        pass

    @abstractmethod
    def correct(self):
        """
        This method is called at the end of a job when an error is detected.
        It should perform any corrective measures relating to the detected
        error.

        This method should return a JSON serializable dict that describes
        the errors and actions taken. E.g.
        {"errors": list_of_errors, "actions": list_of_actions_taken}.
        If this is an unfixable error, actions should be set to None.
        """
        pass

    @abstractproperty
    def is_monitor(self):
        """
        This property indicates whether the error handler is a monitor,
        i.e., a handler that monitors a job as it is running. If a
        monitor-type handler notices an error, the job will be sent a
        termination signal, the error is then corrected,
        and then the job is restarted. This is useful for catching errors
        that occur early in the run but do not cause immediate failure.
        """
        return False

    @property
    def is_terminating(self):
        """
        Whether this handler terminates a job upon error detection. Defaults
        to True. Set to False for non-terminating errors, i.e., errors that
        can be recovered from without terminating a job.
        """
        return True

    @abstractproperty
    def to_dict(self):
        """
        This method should return a JSON serializable dict describing the
        ErrorHandler, and can be deserialized using the from_dict static
        method.
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, d):
        """
        This method should return the ErrorHandler from a dict representation
        of the object given by the to_dict property.
        """
        pass


class Job(object):
    """
    Abstract base class defining the interface for a Job.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def setup(self):
        """
        This method is run before the start of a job. Allows for some
        pre-processing.
        """
        pass

    @abstractmethod
    def run(self):
        """
        This method perform the actual work for the job. If parallel error
        checking is desired, this must return a Popen process.
        """
        pass

    @abstractmethod
    def postprocess(self):
        """
        This method is called at the end of a job, *after* error detection.
        This allows post-processing, such as cleanup, analysis of results,
        etc.
        """
        pass

    @abstractproperty
    def name(self):
        """
        A nice string name for the job.
        """
        pass

    @abstractproperty
    def to_dict(self):
        """
        This method should return a JSON serializable dict describing the
        Job, and can be deserialized using the from_dict static
        method.
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, d):
        """
        This method should return the Job from a dict representation of the
        object given by the to_dict property.
        """
        pass


def backup(filenames, prefix="error"):
    """
    Backup files to a tar.gz file. Used, for example, in backing up the
    files of an errored run before performing corrections.

    Args:
        filenames:
            List of files to backup. Supports wildcards, e.g., *.*.
        prefix:
            prefix to the files. Defaults to error, which means a series of
            error.1.tar.gz, error.2.tar.gz, ... will be generated.
    """
    num = max([0] + [int(f.split(".")[1])
                     for f in glob("{}.*.tar.gz".format(prefix))])
    filename = "{}.{}.tar.gz".format(prefix, num + 1)
    logging.info("Backing up run to {}.".format(filename))
    tar = tarfile.open(filename, "w:gz")
    for fname in filenames:
        for f in glob(fname):
            tar.add(f)
    tar.close()


def gzip_dir(path):
    """
    Gzips all files in a directory. Used, for instance, to compress all
    files at the end of a run.

    Args:
        path:
            Path to directory.
    """
    for f in os.listdir(path):
        if not f.endswith("gz"):
            with open(f, 'rb') as f_in, \
                    GzipFile('{}.gz'.format(f), 'wb') as f_out:
                f_out.writelines(f_in)
            os.remove(f)
