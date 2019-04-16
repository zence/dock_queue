#! /usr/bin/env python3.6
import os
import sys
import re
import pandas as pd
import subprocess as sp

from select import select
from work_queue import *

regex = re.compile(r"(?:(?:\si:\s)(?P<input>[^\s]+))|"
                   r"(?:(?:\so:\s)(?P<output>[^\s]+))|"
                   r"(?:(?:\sp:\s)(?P<priority>[^\s]+))|"
                   r"(?:(?:\sc:\s)(?P<command>[^\s]+))")

#bash_path = "/bin/bash"
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

#user_input = input("Please give a command to add to the queue: ")

#print(user_input, flush=True)

#for i in range(20):
#    infile = "hello_world.sh"
#    outfile = "output%d.txt" % i
#    command = "bash %s %d > %s" % (infile, i, outfile)
#    #command = "echo 'hell world' > %s" % outfile
#    t = Task(command)
#    t.specify_priority(20 - i)
#    t.specify_file(bash_path, "bash", WORK_QUEUE_INPUT, cache=True)
#    t.specify_file("/home/hello_world.sh", infile, WORK_QUEUE_INPUT, cache=False)
#    t.specify_file('/'.join(["/home/output", outfile]), outfile, WORK_QUEUE_OUTPUT, cache=False)
#    taskid = q.submit(t)
#    print("Submitted task (id# %d): %s" % (taskid, t.command), flush=True)

#with open("commands.txt", "r") as in_f:
#    for line in in_f:
#        line = line.split("::end_command::")
#        command = line[0]
#        specs = line[1]
#        specs_df = pd.DataFrame([g.groupdict() for g in regex.finditer(specs)])
#        input_commands = specs_df['command'].dropna().tolist()
#        input_files = specs_df['input'].dropna().tolist()
#        output_files = specs_df['output'].dropna().tolist()
#        priority = specs_df['priority'].dropna().tolist()
#
#        if len(priority) > 0:
#            priority = priority[0]
#        else:
#            priority = 0
#
#        t = Task(command)
#        t.specify_priority(int(priority))
#
#        for input_command in input_commands:
#            cmd_path = sp.run(['which', input_command], stdout=sp.PIPE).stdout.decode().rstrip()
#            print("Command: {}, command location: {}".format(input_command, cmd_path), flush=True)
#            t.specify_file(cmd_path, input_command, WORK_QUEUE_INPUT, cache=True)
#
#        for input_file in input_files:
#            t.specify_file(input_file, input_file.split('/')[-1], WORK_QUEUE_INPUT, cache=False)
#
#        for output_file in output_files:
#            t.specify_file(output_file, output_file.split('/')[-1], WORK_QUEUE_OUTPUT, cache=False)
#
#        task_id = q.submit(t)
#        print("Subbmitted task (id: {}): {} \nPriority: {}".format(task_id, t.command, t.priority), flush=True)
user_input = ""

while user_input != "exit":
    user_input = ""
    t = q.wait(1)
    if t:
        print("task (id# {}) complete: {} (return code {}) at {} by {}".format(t.id, t.command,
                                                                               t.return_status,
                                                                               t.finish_time,
                                                                               t.hostname), flush=True)
        if t.return_status != 0:
            print(t.output)

    rlist, _, _ = select([sys.stdin], [], [], 1)
    if rlist:
        user_input = sys.stdin.readline().rstrip()
    if user_input != "" and user_input != "exit":
        line = user_input.split("::end_command::")
        command = line[0]
        specs = line[1]
        specs_df = pd.DataFrame([g.groupdict() for g in regex.finditer(specs)])
        input_commands = specs_df['command'].dropna().tolist()
        input_files = specs_df['input'].dropna().tolist()
        output_files = specs_df['output'].dropna().tolist()
        priority = specs_df['priority'].dropna().tolist()

        if len(priority) > 0:
            priority = priority[0]
        else:
            priority = 0

        t = Task(command)
        t.specify_priority(int(priority))

        for input_command in input_commands:
            cmd_path = sp.run(['which', input_command], stdout=sp.PIPE).stdout.decode().rstrip()
            print("Command: {}, command location: {}".format(input_command, cmd_path), flush=True)
            t.specify_file(cmd_path, input_command, WORK_QUEUE_INPUT, cache=True)

        for input_file in input_files:
            t.specify_file(input_file, input_file.split('/')[-1], WORK_QUEUE_INPUT, cache=False)

        for output_file in output_files:
            t.specify_file(output_file, output_file.split('/')[-1], WORK_QUEUE_OUTPUT, cache=False)

        task_id = q.submit(t)
        print("Subbmitted task (id: {}): {} \nPriority: {}".format(task_id, t.command, t.priority), flush=True)

sys.exit(0)
