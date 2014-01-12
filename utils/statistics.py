import math

def mean(data):
    return sum(data)/float(len(data))

def median(data):
    return sorted(data)[len(data)/2]

def variance(data):
    avg = mean(data)
    return [(value - avg) ** 2 for value in data]

def std_dev(data):
    return math.sqrt(mean(variance(data)))
