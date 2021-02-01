import os
import subprocess

listfile = "peru13_files_to_recover2_caofs.txt"
listit = [line.strip() for line in open(listfile, 'r')]

for filename in listit:
    result = subprocess.Popen(["fsfileinfo", filename], stdout=subprocess.PIPE)
    out = result.stdout.read()
    outnew = (out.split('\n'))[14]
    tapeid = (outnew.strip().split(':'))[1].strip()

    print("%s, %s" % (filename, tapeid))

