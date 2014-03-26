# -*- coding: UTF-8 -*-
'''
Created on Mar 11, 2014
Incentivization Script Driver Function. Pulls information from files/datamart, outputs
various files for verification/payment

@author: ssmith
@copyright: 2014+
'''

import requests, csv, json, sys, datetime, re, incentivedb, getopt

api = open('api_key', 'r').readline().strip('\n').strip()
configName = "config" # change this to change config file name

def formatDate(dateString):
    '''
    Ensures passed in dates are in proper format
    @type dateString: String
    @param dateString: Date to verify/convert
    @return: datetime or None
    '''
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
    '''
    Gets all keys/values from config file
    @param filename: name of config file
    @type filename: String
    @return: dictionary of type {key:value} from config
    '''
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
    '''
    Get list of all users from datamart
    @param opt: config file options
    @type opt: dict
    @return: json_encoded user list from datamart
    '''
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
    '''
    Get list of all trades from datamart
    @param opt: config file options
    @type opt: dict
    @param start: starting date bounds
    @type start: datetime
    @param end: ending date bounds
    @type end: datetime
    @return: json_encoded trade list from datamart
    '''
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
    '''
    Get list of all comments from datamart
    @param opt: config file options
    @type opt: dict
    @param start: starting date bounds
    @type start: datetime
    @param end: ending date bounds
    @type end: datetime
    @return: json_encoded comment list from datamart
    '''
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
    '''
    Driver
    @param argv: Command line arguments
    @type argv: list
    @return: none
    '''
    global configName
    startstring = ""
    endstring = ""

    #check for command line inputs
    try:
      opts, args = getopt.getopt(argv,"hs:e:",["startdate=","enddate="])
    except getopt.GetoptError:
        #If no arguments, run script assuming startdate == yesterday
        print 'incentivize.py -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>'
        sys.exit()
    #print opts
    for opt, arg in opts:
        if opt == '-h': #Help documentation
            print 'incentivize.py -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>'
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
    if database.printWinLog():
        print "Winner log saved as "+options["winlog"]+".json in folder "+options["internals"]

    #For readability, print previous winners and winner log as CSV files
    if options["out_csv"].lower() == "true":
        if database.printcsv():
            print "CSV files saved in "+options["output_dir"]

    #print winners

    wincounter = 0
    finalWinList = []
    winners = database.winners
    for user,winNum in winners.iteritems():
        '''if wincounter >= 25:
            break
        if options["dupes"] == "true":
             wincounter += winNum
        else:
            wincounter += 1'''
        finalWinList.append(user)
    wincounter = 0
    winwriter = csv.DictWriter(open(options["output_dir"]+"/"+options["newwinners"]+".csv", 'wb'), fieldnames=['user_id', 'num_wins'], delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    for person in finalWinList:
        '''if options["dupes"] == "true":
            numwins = winners[person]
        else:
            numwins = 1'''
        numwins = winners[person]
        wincounter += numwins
        winwriter.writerow({'user_id':person, 'num_wins':numwins})
    winwriter.writerow({'user_id':"Total wins", 'num_wins':wincounter})

if __name__ == '__main__': #driver function
    main(sys.argv[1:])