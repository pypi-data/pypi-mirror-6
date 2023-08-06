#!/usr/bin/python3

#-*-coding:utf-8-*-

def sanitize(time_string):
    if '-' in time_string:
        spliter = '-'
    elif ':' in time_string:
        spliter = ':'
    else:
        return(time_string)
    (mins, secs) = time_string.split(spliter)
    return(mins+'.'+secs)

class AthleteList(list):
    def __init__(self, a_name, a_dob=None, a_times=[]):
        list.__init__([])
        self.name = a_name
        self.dob = a_dob
        self.extend(a_times)
    def top3(self):
        return(sorted(set([sanitize(t) for t in self]))[0:3])
""" def add_time(self, time_value):
        self.times.append(time_value)
    def add_times(self, list_of_times):
        self.times.extend(list_of_times)
"""

def get_coach_data(filename):
    try:
        with open(filename) as f:
            data = f.readline()
        templ = data.strip().split(',')
        return AthleteList(templ.pop(0), templ.pop(0), templ)
    except IOError as ioerr:
        print('File error:' + str(ioerr))
        return(None)

class NameList(list):
    def __init__(self, a_name):
        list.__init__([])
        self.name = a_name

