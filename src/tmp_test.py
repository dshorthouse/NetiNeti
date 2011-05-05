#!/usr/bin/env python
from netineti import NetiNetiTrainer
from netineti import NameFinder
import subprocess
import shlex
import math

def variance(population):
    n = 0
    mean = 0.0
    s = 0.0
    for x in population:
        n = n + 1
        delta = x - mean
        mean = mean + (delta / n)
        s = s + delta * (x - mean)

    # if you want to calculate std deviation
    # of a sample change this to "s / (n-1)"
    return s / (n-1)

# calculate the standard deviation of a population
# accepts: an array, the population
# returns: the standard deviation
def standard_deviation(population):
    return math.sqrt(variance(population))


population = []

for i in range(1, 3):
    print "going through %s cycle" % i
    neti_neti = NetiNetiTrainer()
    name_finder = NameFinder(neti_neti)

    result = name_finder.find_names(open("data/test.txt").read())

    test_result_file = open("data/test_result_after_refactoring.txt", 'w')

    for i in result[1]:
        test_result_file.write(i + "\n")

    test_result_file.close()

    args = shlex.split('diff -d  data/test_result_before_refactoring.txt data/test_result_after_refactoring.txt')
    #print args
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
    #for i in differences:
        #print i
    #print "Found " + str(len(differences)) + " differences"
    population.append(len(differences))

dev = standard_deviation(population)

sum = 0
for i in population:
    sum = sum + i

print "Mean: %s, St. dev: %s" % (float(sum)/float(len(population)), dev)
