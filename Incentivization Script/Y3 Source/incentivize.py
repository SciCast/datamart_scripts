# -*- coding: UTF-8 -*-
'''
Created on Mar 11, 2014


@author: ssmith
'''

import requests, csv, json, sys, datetime, re, incentivedb

api = open('api_key', 'r').readline().strip('\n')
configName = "config" # change this to change config file name

def formatDate(dateString):
    if dateString is not None:
        try:
            retval = datetime.datetime.strptime(dateString, "%m-%d-%Y")
        except ValueError:
            try:
                retval = datetime.datetime.strptime(dateString, "%m/%d/%Y")
            except ValueError:
                try:
                    retval = datetime.datetime.strptime(dateString, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Incorrect date format for "+str(dateString)+". Should be one of YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY")
        return retval
    else:
        return None

def getConfig(filename):
    config = {}
    lines = [line.strip() for line in open(filename)]
    for line in lines:
        if line[0] == "#" or line == "":
            continue
        else:
            parts = line.split(":")
            config[parts[0]] = parts[1]
    return config

def getUsers(opt):
    s = requests.session()
    url = "http://"+opt["url"]+opt["port"]+"/person/?format=json&api_key="+api
    r = s.get(url)
    t = r.text
    #print t
    try:
        o = json.loads(t)
    except ValueError:
        sys.exit("Website return did not match expected format from "+url)
    return o

def getTrades(opt, start, end):
    s = requests.session()
    url = "http://"+opt["url"]+opt["port"]+"/trade_history/?format=json&api_key="+api+"&start_date="+start.strftime('%m-%d-%Y')
    if end:
        url += "&end_date="+end.strftime('%m-%d-%Y')
    r = s.get(url)
    t = r.text
    #print t
    try:
        o = json.loads(t)
    except ValueError:
        sys.exit("Website return did not match expected format from "+url)
    return o

def getComments(opt, start, end):
    s = requests.session()
    url = "http://"+opt["url"]+opt["port"]+"/comment/?format=json&api_key="+api+"&start_date="+start.strftime('%m-%d-%Y')
    if end:
        url += "&end_date="+end.strftime('%m-%d-%Y')
    r = s.get(url)
    t = r.text
    #print t
    try:
        o = json.loads(t)
    except ValueError:
        sys.exit("Website return did not match expected format from "+url)
    return o

def main():
    import getopt
    global configName
    startstring = ""
    endstring = ""

    #check for command line inputs
    try:
      opts, args = getopt.getopt(sys.argv,"hs:e:",["startdate=","enddate="])
    except getopt.GetoptError:
        #If no arguments, run script assuming startdate == yesterday
        yesterday = datetime.date.today()-datetime.timedelta(days=1)
        startstring = yesterday.strftime('%m-%d-%Y')
    for opt, arg in opts:
        if opt == '-h': #Help documentation
            print 'incentivize -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>'
            sys.exit()
        elif opt in ("-s", "--startdate"):
            startstring = arg
        elif opt in ("-e", "--enddate"):
            endstring = arg

    #convert strings into datetime objects
    startDate = formatDate(startstring)

    #I believe end date is optional, for ranges only
    if (endstring):
        endDate = formatDate(endstring)
    else:
        endDate = None

    options = getConfig(configName)
    users = getUsers(options)
    trades = getTrades(options, startDate, endDate)
    comments = getComments(options, startDate, endDate)

    #Compile everything into a Database object
    database = incentivedb(options, users, trades, comments, startDate, endDate)

    #Calculate our accumulation for the time period (if necessary)
    database.getAccumulation()

    winners = database.calculateWinners()


if __name__ == '__main__': #driver function
    main()