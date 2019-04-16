#! /usr/bin/env python3.6
import os
import sys
import subprocess as sp
import argparse

from work_queue import *


def make_queue():
    cmd = sys.argv[1]
    cmd_args = sys.argv[2:]
    cmd_path = sp.run(['which', cmd], stdout=sp.PIPE).stdout.decode().rstrip()
    #if not os.path.exists(bash_path):
    #    bash_path = "/usr/bin/bash"
    #    if not os.path.exists(bash_path):
    #        print("Command 'echo' not found. I've got a bad feeling about this...", flush=True)
    #        sys.exit(1)

    try:
        q = WorkQueue(9123)
    except:
        print("Instantiation of Work Queue failed!", flush=True)
        sys.exit(1)

    print("listening on port {}".format(q.port), flush=True)

    for i in range(20):
        outfile = "output%d.txt" % i
        #command = "%s %s" % (cmd, cmd_args)
        command = "ls -lha input_data > %s" % outfile
        t = Task(command)
        t.specify_file(cmd_path, cmd, WORK_QUEUE_INPUT, cache=True)
        t.specify_file("/home/input_data", "input_data", WORK_QUEUE_INPUT, cache=False)
        t.specify_file('/'.join(["/home/output", outfile]), outfile, WORK_QUEUE_OUTPUT, cache=False)
        taskid = q.submit(t)
        print("Submitted task (id# %d): %s" % (taskid, t.command), flush=True)

    while not q.empty():
        t = q.wait(5)
        if t:
            print("task (id# %d) complete: %s (return code %d)" % (t.id, t.command, t.return_status), flush=True)
            if t.return_status != 0:
                None

    sys.exit(0)


if __name__ == "__main__":
    make_queue()
