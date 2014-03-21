# -*- coding: UTF-8 -*-
'''
Created on Mar 11, 2014


@author: ssmith
'''

import requests, csv, json, sys, datetime, re, incentivedb, getopt

api = open('api_key', 'r').readline().strip('\n').strip()
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
        if len(line) == 0 or line[0] == "#":
            continue
        else:
            parts = line.split(":")
            config[parts[0]] = parts[1]
    return config

def getUsers(opt):
    s = requests.session()
    url = "http://"+opt["url"]+":"+opt["port"]+"/person/?format=json&api_key="+api
    r = s.get(url)
    t = r.text
    #print t
    try:
        o = json.loads(t)
    #sys.exit(1)
    except ValueError:
        sys.exit("Website return did not match expected format from "+url)
    return o

def getTrades(opt, start, end):
    s = requests.session()
    url = "http://"+opt["url"]+":"+opt["port"]+"/trade_history/?format=json&api_key="+api+"&start_date="+start.strftime('%m-%d-%Y')
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
    url = "http://"+opt["url"]+":"+opt["port"]+"/comment/?format=json&api_key="+api+"&start_date="+start.strftime('%m-%d-%Y')
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

def main(argv):
    global configName
    startstring = ""
    endstring = ""

    #check for command line inputs
    try:
      opts, args = getopt.getopt(argv,"hs:e:",["startdate=","enddate="])
    except getopt.GetoptError:
        #If no arguments, run script assuming startdate == yesterday
        print 'incentivize -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>'
        sys.exit()
    #print opts
    for opt, arg in opts:
        if opt == '-h': #Help documentation
            print 'incentivize -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>'
            sys.exit()
        elif opt in ("-s", "--startdate"):
            startstring = arg
        elif opt in ("-e", "--enddate"):
            endstring = arg

    if not startstring:
        yesterday = datetime.date.today()-datetime.timedelta(days=1)
        startstring = yesterday.strftime('%m-%d-%Y')
        endstring = startstring

    #convert strings into datetime objects
    startDate = formatDate(startstring)

    #I believe end date is optional, for ranges only
    if (endstring):
        endDate = formatDate(endstring)
    else:
        endDate = startDate

    print str(startDate)+" "+str(endDate)
    options = getConfig(configName)
    print "Getting users"
    users = getUsers(options)
    print "Users received, getting trades"
    trades = getTrades(options, startDate, endDate)
    print "Trades received, getting comments"
    comments = getComments(options, startDate, endDate)
    print "Comments received"
    print "Forming database"

    #Compile everything into a Database object
    database = incentivedb.IncentiveDB(options, users, trades, comments, startDate, endDate)

    print "Tabulating accumulation"
    #Calculate our accumulation for the time period (if necessary)
    database.getAccumulation()

    print "Getting winners"
    winners = database.calculateWinners()

    winList = []

    for user,winNum in winners.iteritems():
        winList.append(database.getUsername(user))

    #Now we have the winners, let's work on our outputs
    if database.printDatabase():
        print "Previous db saved as "+options["db"]+".json in folder "+options["internals"]

    #Keep track of the winners
    f = None
    try:
        f = open(options["winlog"]+".json")
    except IOError:
        print 'No win log file'
    if database.printWinLog(f):
        print "Winner log saved as "+options["winlog"]+".json in folder "+options["internals"]

    #For readability, print previous winners and winner log as CSV files
    if options["outcsv"].lower() == "true":
        if database.printcsv():
            print "CSV files saved in "+options["output_dir"]

    #print winners

    test = 0


    #print winList


if __name__ == '__main__': #driver function
    main(sys.argv[1:])