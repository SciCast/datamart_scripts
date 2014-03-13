# -*- coding: UTF-8 -*-

import json, random, math
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
        self.accumulate = True if opt["accumulation"] == "true" else False
        self.previous = self.getPrevious(opt)
        self.numwinners = opt["winners"]
        self.debug = opt["debug"]
        self.ignore = opt["ignore"].split(',')
        self.activity = {}
        self.activitytype = opt["activity"]
        self.startdate = start
        self.enddate = end
        self.winners = {}


    def getPrevious(self,opt):
        filename = opt["db"]
        if os.path.isfile(filename):
            json_data = open(filename)
            data = json.load(json_data)
            json_data.close()
        else:
            data = None
        return data

    def getAccumulation(self):
        if self.previous is not None:
            self.activity = self.previous
        for user in self.users:
            skip = False
            for key, value in user.iteritems():
                for item in self.ignore:
                    if item in value:
                        skip = True
            if skip:
                continue
            user_id = str(user["user_id"])
            if user_id in self.activity:
                self.activity[user_id][self.activitytype] += self.countActivity(user_id)
            else:
                self.activity[user_id][self.activitytype] = self.countActivity(user_id)
                if self.activitytype == "trades":
                    self.activity[user_id]["comments"] = 0
                else:
                    self.activity[user_id]["trades"] = 0

    def countActivity(self, user_id):
        counter = 0
        if self.activitytype == "trades":
            previousTrade = None
            for trade in self.trades:
                if trade["user_id"] == user_id:
                    if previousTrade is not None:
                        counter += 1
                    else:
                        if previousTrade["user_id"] != user_id:
                            counter += 1
                            previousTrade = trade
                        else:
                            previousTrade = trade
        elif self.activitytype == "comments":
            for comment in self.comments:
                if comment["user_id"] == user_id:
                    counter += 1
        return counter

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
            if activeList[self.activityType] > 0:
                entries = 1+log(activeList[self.activityType], 2)
                hat[user] = entries
        randomizer = WeightedRandomizer(hat)
        while len(winners) <= self.numwinners:
            win = randomizer.random()
            if winners[win]:
                winners[win] += 1
            else:
                winners[win] = 1
        self.winners = winners

        return self.winners

