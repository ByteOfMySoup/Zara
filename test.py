import subprocess
import os


def run(content):
    cmd = content.replace("|sys|", "")
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, error = p.communicate()
    return output, error


r = run("|sys|s")
print(r)
