#!/usr/bin/env python
import os
import subprocess
import sys
import yaml

if len(sys.argv) == 1:
    print("""\
Usage: metafig.py [command] [stack] [parameters...] < metafig.yml
Available commands:
- list
- gen-to-stdout
- gen-to-volume
- build-and-tag
- any fig command""")
    exit()

stacks = yaml.load(sys.stdin)

command = sys.argv[1]

if command == "list":
    print("Available stacks:")
    for stackname in sorted(s for s in stacks if type(stacks[s]) == str):
        print("- {}".format(stackname))
    exit()

stack = sys.argv[2]

if stack not in stacks:
    print("Unknown stack.")
    exit()

if type(stacks[stack]) != str:
    print("{!r} does not seem to be a stack.".format(stack))
    exit()

components = stacks[stack].split()
newstack = dict()
for component in components:
    if component not in stacks:
        print("Stack {!r} references unknown component {!r}."
              .format(stack, component))
        exit()
    newstack[component] = stacks[component]

if command == "gen-to-stdout":
    yaml.dump(newstack, sys.stdout)
    exit()

if command == "gen-to-volume":
    with open("/metafig/{}.yml".format(stack), "w") as f:
        yaml.dump(newstack, f)
    exit()

devnull = open("/dev/null", "w")

try:
    subprocess.check_call(["docker", "info"],
                          stdout=devnull, stderr=devnull)
except Exception as e:
    print("An error occurred while executing docker info. Aborting.")
    print(e)

# FIXME: clean that up
tmp = "/tmp/tmpmetafig.yml"
with open(tmp, "w") as f:
    yaml.dump(newstack, f)

if command == "build-and-tag":
    tag = sys.argv[3]
    subprocess.check_call(["fig", "-p", stack, "-f", tmp, "build"])
    for component in components:
        old_name = "{}_{}".format(stack, component)
        new_name = "{}_{}:{}".format(stack, component, tag)
        print("Tagging {!r} as {!r}".format(old_name, new_name))
        subprocess.check_call(["docker", "tag", old_name, new_name])
    exit()

subprocess.check_call(["fig", "-p", stack, "-f", tmp, command]
                      + sys.argv[4:])
