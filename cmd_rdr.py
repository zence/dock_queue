#! /usr/bin/env python3.6
import os
import sys
import re
import argparse
import pandas as pd
import subprocess as sp

from work_queue import *

REGEX = re.compile(r"(?:(?:\si:\s)(?P<input>[^\s]+))|"
                   r"(?:(?:\so:\s)(?P<output>[^\s]+))|"
                   r"(?:(?:\sp:\s)(?P<priority>[^\s]+))|"
                   r"(?:(?:\sc:\s)(?P<command>[^\s]+))")
EPILOG = '''
Commands within the input_file must be formatted as follows:
<command> ::end_command:: <files to be used> <priority>

<files to be used> include any input and output files required for specific
command and should be prefaced with the appropriate tag as follows:

i: <input file>[str]
o: <output file>[str]
p: <priority>[int]

<priority> MUST be the final specification or the command will fail
'''


def parse_arguments():
    args = argparse.ArgumentParser(description="Work Queue (file reader)",
                                   add_help=True,
                                   epilog=EPILOG,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    args.add_argument('-p', '--port', required=True, type=int,
                      help="The desired port to which work queue will be attached")
    args.add_argument('-i', '--input_file', required=True, type=str,
                      help='Input file containing commands')

    return args.parse_args()


def main():
    args = parse_arguments()

    try:
        q = WorkQueue(args.port)
    except:
        print("Instantiation of Work Queue failed!", flush=True)
        sys.exit(1)

    print("listening on port {}".format(q.port), flush=True)

    with open("/".join(["/home/input", args.input_file]), "r") as in_f:
        for line in in_f:
            line = line.split("::end_command::")
            command = line[0]
            specs = line[1]
            specs_df = pd.DataFrame([g.groupdict() for g in REGEX.finditer(specs)])
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

    while not q.empty():
        t = q.wait(5)
        if t:
            print("task (id# {}) complete: {} (return code {}) at {} by {}".format(t.id, t.command,
                                                                                   t.return_status,
                                                                                   t.finish_time,
                                                                                   t.hostname), flush=True)
            if t.return_status != 0:
                print(t.output)

    sys.exit(0)


if __name__ == "__main__":
    main()
