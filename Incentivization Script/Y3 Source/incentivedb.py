# -*- coding: UTF-8 -*-

'''
Created on March 11, 2014
Incentivization database, the workhorse. Calculates activity with accumulation, previous
winners, etc.

@author: Scott Smith
@copyright: 2014+
'''


import json, random, math, os, sys, datetime, csv
from collections import OrderedDict

class IncentiveDB():
    '''
    Created class to handle the activities necessary for the incentivization script.
    '''
    def __init__(self, opt, users, trades, comments, start = None, end = None):
        '''
        Initializes database
        @param opt: config options from config file
        @type opt: dict
        @param users: all users pulled from datamart
        @type users: json (list of dict objects)
        @param trades: all trades between time intervals
        @type trades: json (list of dict objects)
        @param comments: all comments made between time intervals
        @type comments: json (list of dict objects)
        @param start: beginning date bound
        @type start: datetime or None if not passed in
        @param end: ending date bound
        @type end: datetime or None if not passed in
        @return: none
        '''
        self.users = users
        self.trades = trades
        self.comments = comments
        self.opt = opt
        self.accumulate = True if opt["accumulate"] == "true" else False
        self.previous = self.getPrevious(opt)
        self.prevwinners = self.getPreviousWinners(opt)
        self.numwinners = opt["winners"]
        self.debug = opt["debug"]
        self.ignore = opt["ignore"].split(',')
        self.activity = {}
        self.startdate = start
        self.enddate = end
        self.winners = {}
        self.previousActivity = None
        self.hat = {}
        self.winlog = {}


    def getPrevious(self,opt):
        '''
        Gets list of previous users, used for accumulation levels
        @param opt: config file options
        @type opt: dict
        @return: information inside database file or None if file doesn't exist
        '''
        filename = opt["db"]+".json"
        if os.path.isfile(filename):
            json_data = open(filename)
            data = json.load(json_data)
            json_data.close()
            print type(data)
        else:
            data = None
        return data

    def getPreviousWinners(self,opt):
        '''
        Gets list of previous winners, for keeping track of who's won
        @param opt: config file options
        @type opt: dict
        @return: information inside previous winners file or None if file doesn't exist
        '''
        filename = opt["winlog"]+".json"
        if os.path.isfile(filename):
            json_data = open(filename)
            data = json.load(json_data)
            json_data.close()
            print type(data)
        else:
            data = None
        return data

    def getAccumulation(self):
        '''
        Gets accumulation value. This is a combination of previous accumulation (if exists
        and accumulate is set in config file), and the number of ACTIVITY_TYPE for current run
        @return: none
        '''

        if self.previous is not None and self.accumulate:
            print type(self.previous)
            self.activity = dict((int(k), v) for k,v in self.previous.iteritems())
        for user in self.users:
            skip = False
            for key, value in user.iteritems():
                for item in self.ignore:
                    if unicode(value).lower().find(unicode(item).lower()) != -1:
                        print "Skipped: "+value
                        skip = True
            if skip:
                continue
            user_id = user["user_id"]
            #print self.activity
            if user_id in self.activity:
                temp = self.countActivity(user_id)
                for type,idlist in temp.iteritems():
                    if type in self.activity[user_id]:
                        self.activity[user_id][type].append(idlist)
                    else:
                        self.activity[user_id][type] = idlist
            else:
                self.activity[user_id] = self.countActivity(user_id)

    def countActivity(self, user_id):
        '''
        Utility function for getAccumulation to get current activity levels for current run
        @param user_id: user to check activity levels of
        @type user_id: integer
        @return: integer describing activity levels for current run
        '''

        tradecounter = []
        commentcounter = []
        for trade in self.trades:
            if trade["user_id"] == user_id:
                if self.previousActivity is None:
                    tradecounter.append(trade["id"])
                else:
                    if self.previousActivity["user_id"] != user_id:
                        tradecounter.append(trade["id"])
                        self.previousActivity = trade
                    else:
                        self.previousActivity = trade
        for comment in self.comments:
            if comment["user_id"] == user_id:
                if self.previousActivity is None:
                    commentcounter.append(comment["id"])
                else:
                    if self.previousActivity["user_id"] != user_id:
                        commentcounter.append(comment["id"])
                        self.previousActivity = comment
                    else:
                        self.previousActivity = comment
        return {"trades":tradecounter,"comments":commentcounter}

    def printDatabase(self):
        '''
        Utility function to print activity levels, used for accumulation and some tracking
        @return: none
        '''
        self.previous = self.activity
        folder = self.opt["internals"]
        winNum = 0
        if not os.path.exists(folder):
            os.makedirs(folder)
        for key, value in self.previous.iteritems():
            #print str(key in self.winners)+" "+str(key)
            if key in self.winners and self.accumulate:
                #print "Found: "+str(key)+" "+self.activitytype
                for type in value:
                    type = 0
        try:
            js = open(folder+"/"+self.opt["db"]+".json",'w')
            json.dump(self.previous, js, sort_keys=True, indent=4)
            js.close()
            return True
        except ValueError:
            print "Error"

    def printWinLog(self):
        '''
        Utility function to print the log of winners. Used for tracking/verifications
        @return: none
        '''
        prev_winners = {}
        today = datetime.datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        folder = self.opt["internals"]
        file_handle = None
        winNum = 0
        try:
            file_handle = open(folder+"/"+self.opt["winlog"]+".json")
        except IOError:
            print 'No win log file'
        if not os.path.exists(folder):
            os.makedirs(folder)
        if file_handle is not None:
            data = json.load(file_handle)
            file_handle.close()
            prev_winners = data
            for key,val in self.winners.iteritems():
                if key in prev_winners:
                    prev_winners[key][today_str] = val
                else:
                    prev_winners[key] = {today_str:val}
        else:
            prev_winners = {}
            for key,val in self.winners.iteritems():
                prev_winners[key] = {today_str:val}
        self.winlog = prev_winners
        try:
            js = open(folder+"/"+self.opt["winlog"]+".json",'w')
            json.dump(self.winlog, js, sort_keys=True, indent=4)
            js.close()
            return True
        except ValueError:
            print "Error"

    def printcsv(self):
        '''
        Prints activity database and previous winners as csv files for easy verification
        @return: none
        '''
        folder = self.opt["output_dir"]
        if not os.path.exists(folder):
            os.makedirs(folder)

        #print the "prevusers" database. Database is used for storing accumulation. This is mostly for debugging
        #or verification
        prevwriter = csv.DictWriter(open(folder+"/"+self.opt["db"]+".csv.txt", 'wb'), fieldnames=['user_id', 'activity_levels'], delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        prevwriter.writeheader()
        for uid,activity in self.previous.iteritems():
            prevwriter.writerow({'user_id':uid, 'activity_levels':activity})

        #print the winner log
        winlogwriter = csv.DictWriter(open(folder+"/"+self.opt["winlog"]+".csv.txt", 'wb'), fieldnames=['user_id', 'win_dates'], delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        winlogwriter.writeheader()
        for uid,dates in self.winlog.iteritems():
            winlogwriter.writerow({'user_id':uid, 'win_dates':dates})

    def getUsername(self,user_id):
        '''
        Gets username for user
        @param user_id: user to pull from database
        @type user_id: integer
        @return: either username or "User not found $user_id"
        '''
        for user in self.users:
            if user["user_id"] == user_id:
                return user["username"]
        return "User not found: "+user_id

    def calculateWinners(self):
        '''
        Meat of the database function. This calculates the winners, based on accumulated
        activity levels and whether or not duplications are allowed.

        @summary: for each activity level, adds an entry in the "hat". Creates a weighted
        random object from the "hat", then adds them to a temporary winner list. If dupes are allowed,
        it gets a list of winners where the number of wins == number of wins allowed in the config
        file
        @return: dict of winners as {user_id:#wins}
        '''

        hat = []
        temp = {}
        #winners = {}
        allUsers = self.activity
        #wincount = 0
        for user, activeList in allUsers.iteritems():
            total_activity = 0
            for type,number in activeList.iteritems():
                total_activity += len(number)
            if total_activity > 0:
                #entries = total_activity
                #for i in range(entries):
                #    hat.append(user)
                #hat[user] = math.ceil(entries)
                for type,number in activeList.iteritems():
                    for id in number:
                        hat.append({ "uid":id, "type": type, "activity": id})
                #wincount += math.ceil(entries)
        if len(hat) < int(self.numwinners):
            print "Not enough people to fill slots"
            print hat
        #    #sys.exit(1)
        if len(hat) == 0:
            print "No valid users"
            print allUsers
            sys.exit(1)
        #randomizer = WeightedRandomizer(hat)
        while len(temp) < int(self.numwinners) and len(hat)>0:
            #win = randomizer.random()
            num = random.randint(0,len(hat)-1)
            win = hat[num]
            if win["uid"] in temp:
                if win["type"] in win["uid"]:
                    win["type"].append(win["activity"])
                else:
                    win["type"] = [win["activity"]]
                #temp[win] += 1
            else:
                temp[win["uid"]] = { win["type"]:[ win["activity"] ] }
            del hat[num]
        #winners = temp
        '''var = False
        for winner,winNum in temp.iteritems():
            if var:
                break
            winners[winner] = 0
            for i in xrange(winNum):
                if var:
                    break
                winners[winner] += 1
                wincount += 1
                if wincount == self.numwinners:
                    var = True'''
        print temp
        self.hat = hat
        self.winners = temp
        return self.winners

