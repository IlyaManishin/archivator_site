import subprocess

def func(a):
    if a == 0:
        subprocess.call(["sudo", "rm", "-rf"])