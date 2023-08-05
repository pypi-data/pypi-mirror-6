#!/usr/bin/env python

import os
import subprocess
INITIAL_PROJECT_PATH = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

# copies a skeleton project in the startproject directory into a new directory
def startproject(projectname):
    print("Creating project...")
    subprocess.call(["cp", "-r", os.path.join(INITIAL_PROJECT_PATH, "lib/python2.7/site-packages/startproject/"), "."])
    subprocess.call(["mv", "startproject", projectname])
    print("Project creation successful!")

def main(argv):
    try:
        if argv[1] == "startproject":
            try:
                startproject(argv[2])
            except IndexError:
                print("Please enter a project name after 'startproject'.")
        else:
            print("Please enter a valid command. So far startproject is the only one")
    except IndexError:
        print("Please enter a valid command.  So far startproject is the only one.")
    return 0

if __name__=="__main__":
    import sys
    code = main(sys.argv)
    sys.exit(code)
