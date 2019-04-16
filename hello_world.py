#! /usr/bin/env python3.6
import os
import sys

from work_queue import *

bash_path = "/bin/bash"
if not os.path.exists(bash_path):
    bash_path = "/usr/bin/bash"
    if not os.path.exists(bash_path):
        print("Command 'echo' not found. I've got a bad feeling about this...", flush=True)
        sys.exit(1)

try:
    q = WorkQueue(9123)
except:
    print("Instantiation of Work Queue failed!", flush=True)
    sys.exit(1)

print("listening on port {}".format(q.port), flush=True)

for i in range(20):
    infile = "hello_world.sh"
    outfile = "output%d.txt" % i
    command = "bash %s %d > %s" % (infile, i, outfile)
    #command = "echo 'hell world' > %s" % outfile
    t = Task(command)
    t.specify_priority(20 - i)
    t.specify_file(bash_path, "bash", WORK_QUEUE_INPUT, cache=True)
    t.specify_file("/home/hello_world.sh", infile, WORK_QUEUE_INPUT, cache=False)
    t.specify_file('/'.join(["/home/output", outfile]), outfile, WORK_QUEUE_OUTPUT, cache=False)
    taskid = q.submit(t)
    print("Submitted task (id# %d): %s" % (taskid, t.command), flush=True)

while not q.empty():
    t = q.wait(5)
    if t:
        print("task (id# {}) complete: {} (return code {}) at {} by {}".format(t.id, t.command,
                                                                               t.return_status,
                                                                               t.finish_time,
                                                                               t.hostname), flush=True)
        if t.return_status != 0:
            print(t.output, flush=True)

sys.exit(0)
