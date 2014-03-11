# -*- coding: UTF-8 -*-

import json, random
from collections import OrderedDict

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
                if value in self.ignore:
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

    def calculateWinners(self):
        #winners = random.sample(winList, sample_size)
        hat = {}

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

        return self.winners

