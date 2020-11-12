import os
import argparse
import subprocess
import fileinput
#from termcolor import colored

found = False
original_commit = ""
def reset_git():
    subprocess.check_output(["git","reset","--hard",original_commit])

import atexit
atexit.register(reset_git)

def execute_evaluate_function() -> bool:
	#write your function here
	file = open("android/scripts/unix/build-qemu-android.sh","r")
	filedata = file.read()
	file.close()

	filedata = filedata.replace('LIBUSB_FLAGS="--enable-libusb --enable-usb-redir"','LIBUSB_FLAGS="--disable-libusb --disable-usb-redir"')
	filedata = filedata.replace('--disable-spice','--disable-usb-redir \\\n	--disable-spice')

	#print(filedata)
	file = open("android/scripts/unix/build-qemu-android.sh","w")
	file.write(filedata)
	file.close()
	#print(filedata)
	build_output = subprocess.Popen(["android/scripts/unix/build-qemu-android.sh","--verbose","--host=linux-x86_64"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = build_output.communicate()
	stdout=stdout.decode('utf-8')
	#print(stdout)
	#print(stderr)
	stderr = stderr.decode('utf-8')
	check = "arm-softmmu/qemu-system-arm!!"
	if (check in stdout) or (check in stderr):
		return False
	else:
		print(build_output)
		return True

def commit_search(commits):
	global found
	if len(commits) == 1:
		print(f"{commits[0][0]} matches")
		exit(1)
	index=(len(commits)-1)//2
	commit = commits[index]
	print(f"\033[93m[ * ]  Testing for commit {commit[0]}\033[0m")
	subprocess.check_output(["git","reset","--hard",commit[0]])
	if execute_evaluate_function():
		found = True
		print("\033[92mTrue\033[0m")
		commit_search(commits[:(index+1)])
	else:
		print("\033[91mFalse\033[0m")
		commit_search(commits[index+1:])

parser = argparse.ArgumentParser()

parser.add_argument("--dir",help="The git directory")
parser.add_argument("--start", help="commit id of the latest commit to start with")
parser.add_argument("--end", help="commit id of the commit to end with")
parser.add_argument("--treesearch", help="search for the breaking commit in a tree shape")
args = parser.parse_args()

directory = os.getcwd()

if args.dir:
	directory = os.path.realpath(args.dir)
os.chdir(directory)

git_output = subprocess.check_output(["git","log","--oneline"]).decode('utf-8')

commit_lines = git_output.split("\n")
commits = []
for line in commit_lines:
	commits.append((line[:10],line[11:]))

original_commit = commits[0][0]

if args.start:
	start_commit = args.start[:10]
	found = False
	for i, j in enumerate(commits):
		if j[0] == start_commit:
			commits=commits[i:]
			found = True
			break
	if not found:
		print("start commit not found")

if args.end:
	end_commit = args.end[:10]
	found = False
	for i, j in enumerate(commits):
		if j[0] == end_commit:
			commits = commits[:i+1]
			found = True
			break
	if not found:
		print("end commit not found")


if args.treesearch:
	commit_search(commits)
#main loop
else:
	for i, commit in enumerate(commits):
		print(f"\033[93m[ * ]  Testing for commit {commit[0]}\033[0m")
		subprocess.check_output(["git","reset","--hard",commit[0]])
		if execute_evaluate_function():
			print(f"Commit {commit[0]} with message {commit[1]} does succeed at the evaluation function")




