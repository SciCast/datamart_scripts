# -*- coding: UTF-8 -*-

import json, random, math, os, sys
from collections import OrderedDict

class WeightedRandomizer:
    def __init__ (self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items ():
            self.__max += weight
            self.__weights.append ( (self.__max, value) )

    def random (self):
        r = random.random () * self.__max
        for ceil, value in self.__weights:
            if ceil > r: return value

class IncentiveDB():
    def __init__(self, opt, users, trades, comments, start = None, end = None):
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
        self.activitytype = opt["activity"]
        self.startdate = start
        self.enddate = end
        self.winners = {}
        self.previousTrade = None
        self.hat = {}


    def getPrevious(self,opt):
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
        filename = opt["prev"]+".json"
        if os.path.isfile(filename):
            json_data = open(filename)
            data = json.load(json_data)
            json_data.close()
            print type(data)
        else:
            data = None
        return data

    def getAccumulation(self):
        if self.previous is not None and self.accumulate:
            print type(self.previous)
            self.activity = dict((int(k), v) for k,v in self.previous.iteritems())
        for user in self.users:
            skip = False
            for key, value in user.iteritems():
                for item in self.ignore:
                    if str(value).lower().find(str(item).lower()) != -1:
                        print "Skipped: "+value
                        skip = True
            if skip:
                continue
            user_id = user["user_id"]
            #print self.activity
            if user_id in self.activity:
                self.activity[user_id][self.activitytype] += self.countActivity(user_id)
            else:
                #print type(user_id)
                self.activity[user_id] = {self.activitytype:self.countActivity(user_id)}
                if self.activitytype == "trades":
                    self.activity[user_id]["comments"] = 0
                else:
                    self.activity[user_id]["trades"] = 0

    def countActivity(self, user_id):
        counter = 0
        if self.activitytype == "trades":
            for trade in self.trades:
                if trade["user_id"] == user_id:
                    if self.previousTrade is None:
                        counter += 1
                    else:
                        if self.previousTrade["user_id"] != user_id:
                            counter += 1
                            self.previousTrade = trade
                        else:
                            self.previousTrade = trade
        elif self.activitytype == "comments":
            for comment in self.comments:
                if comment["user_id"] == user_id:
                    counter += 1
        return counter

    def printDatabase(self):
        self.previous = self.activity
        for key, value in self.previous.iteritems():
            print str(key in self.winners)+" "+str(key)
            if key in self.winners and self.accumulate:
                print "Found: "+str(key)+" "+self.activitytype
                value[self.activitytype] = 0
        try:
            js = open(self.opt["db"]+".json",'w')
            json.dump(self.previous, js, sort_keys=True, indent=4)
            js.close()
            return True
        except ValueError:
            print "Error"

    def printPrevious(self):
        ###TODO###
        #create functionality like above to print previous winners in winner log

        self.previous = self.activity
        for key, value in self.previous.iteritems():
            print str(key in self.winners)+" "+str(key)
            if key in self.winners and self.accumulate:
                print "Found: "+str(key)+" "+self.activitytype
                value[self.activitytype] = 0
        try:
            js = open(self.opt["db"]+".json",'w')
            json.dump(self.previous, js, sort_keys=True, indent=4)
            js.close()
            return True
        except ValueError:
            print "Error"

    def getUsername(self,user_id):
        for user in self.users:
            if user["user_id"] == user_id:
                return user["username"]
        return "User not found: "+user_id

    def calculateWinners(self):

        '''
        TODO Goal: For each user whose activity is >5th percentile and <95th percentile
        add to hat <activity> times

        if activity < 5th percentile:
        if activity >= 1, add to hat 5th percentile times
        *REQUIRES VERIFICATION*

        #get our percentiles for cutoff
        highpercent = 100
        lowpercent = 0
        if self.opt["percent_range"]:
            highpercent -= int(self.opt["percent_range"])
            lowpercent += int(self.opt["percent_range"])
        if self.opt["high_percent"]:
            highpercent = int(self.opt["high_percent"])
        if self.opt["low_percent"]:
            lowpercent = int(self.opt["low_percent"])
        if lowpercent > highpercent:
            temp = lowpercent
            lowpercent = highpercent
            highpercent = temp

        allUsers = self.activity
        sorted_activity = OrderedDict(sorted(allUsers.items(), key=lambda t: t[1]))
        numUsers = len(sorted_activity)
        highPercentile = numUsers * (highpercent/100)
        max_tix = max(sorted_activity[highPercentile],)
        '''

        #winners = random.sample(winList, sample_size)
        #winners calculated by 1+log(activity,2) = shares in hat
        hat = {}
        winners = {}
        allUsers = self.activity
        for user, activeList in allUsers.iteritems():
            if activeList[self.activitytype] > 0:
                entries = 1+math.log(activeList[self.activitytype], 2)
                hat[user] = math.ceil(entries)
        if len(hat) < int(self.numwinners):
            print "Not enough people to win"
            print hat
            sys.exit(1)
        randomizer = WeightedRandomizer(hat)
        while len(winners) < int(self.numwinners):
            win = randomizer.random()
            if win in winners:
                winners[win] += 1
            else:
                winners[win] = 1
        self.hat = hat
        self.winners = winners
        return self.winners

