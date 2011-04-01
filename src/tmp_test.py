#!/usr/bin/env python
from netineti import NetiNetiTrainer
from netineti import NameFinder
import subprocess
import shlex

neti_neti = NetiNetiTrainer()
name_finder = NameFinder(neti_neti)

result = name_finder.find_names(open("data/test.txt").read())

test_result_file = open("data/test_result_after_refactoring.txt", 'w')

for i in result[1]:
    test_result_file.write(i + "\n")

test_result_file.close()

args = shlex.split('diff -d  data/test_result_before_refactoring.txt data/test_result_after_refactoring.txt')
print args
result = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
result = result[0].split("\n")
ins = []
outs = []
for i in result:
    if len(i) > 0:
        if i[0] == '>':
            outs.append(i.strip())
        if i[0] == '<':
            ins.append(i.strip())
    differences = ins + outs
for i in differences:
    print i
print "Found " + str(len(differences)) + " differences"

