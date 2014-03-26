# -*- coding: UTF-8 -*-

'''
Created on Mar 24, 2014


@author: ssmith
'''

import sys, datetime, requests, json

class suite():
    def __init__(self, test=-1, startdate=None, enddate=None, aggregate_level="", filename="config"):
        """
        Section 1
        =========
        @type test: integer
        @param test: integer describing which test to do out of list:
        ["comment","person","leaderboard","question","question_history","trade_history"]
        if test is -1, do all tests
        @type startdate: either datetime or None
        @param startdate: date parameter to filter returned data or None if not filtering
        @type enddate: either datetime or None
        @param enddate: date parameter to filter returned data or None if not filtering
        @type aggregate_level: String
        @param aggregate_level: daily, weekly, monthly, or yearly
        @type filename: String
        @param filename: config filename, "config" by default if not passed
        @return: None

        Section 2
        =========
            Initialize test suite. Default variables will run all tests with no options
        """

        self.test = test
        self.startdate = startdate
        self.enddate = enddate
        self.aggregate_level = aggregate_level
        self.options = self.getConfig()
        self.api = open('api_key', 'r').readline().strip('\n')
        self.testList = ["comment","person","leaderboard","question","question_history","trade_history"]

    def getConfig(self, filename="config"):
        """
        @type filename: String
        @param filename: name of config file, "config" by default
        @return: dictionary of {option:value} from the config file
        """
        config = {}
        lines = [line.strip() for line in open(filename)]
        for line in lines:
            if len(line) == 0 or line[0] == "#":
                continue
            else:
                parts = line.split(":")
                config[parts[0]] = parts[1]
        return config

    def getData(self,targetUrl):
        """
        Does a call to targetUrl, parses result to json, returns the json

        @type targetUrl: String
        @param targetUrl: URL to pull data from, with options, etc
        @return: JSON object with results of query
        """

        print "Receiving: "+targetUrl
        s = requests.session()
        r = s.get(targetUrl)
        t = r.text
        #print t
        try:
            o = json.loads(t)
        except ValueError:
            print "Website return did not match expected format: "+t
            sys.exit()
        return o

    def formatDate(self, dateObject):
        """
        Convert the date given in the command line argument into a proper format for the
        datamart API

        @type dateObject: datetime object
        @param dateObject: Date to be converted
        @return: Date converted into proper format or None if there's an error
        """
        retval = ""
        try:
            retval = dateObject.strftime("%m-%d-%Y")
        except ValueError:
            print "Error with date "+str(dateObject)
            retval = None
        return retval

    def sanity(self, test = -2):
        """
        Do sanity checks. This verifies several things:
            -No returned object contains more keys than any other object
            -No duplicate ID numbers
            -All value types are what is expected
                -eg value is not an integer if it is supposed to be a string
        Test indexes reference:
        ["comment","person","leaderboard","question","question_history","trade_history"]

        @type test: integer
        @param test: test suite to run. If no argument, it will run whateve ris set as self.test
        @return:
        """
        testUrl = ""
        if test == -2:
            test = self.test
        elif test == -1:
            for i in range(5):
                self.sanity(i)
        else:
            url = "http://"+self.options["url"]+":"+self.options["port"]+"/"
            testName = self.testList[test]
            if test == 2:
                testUrl = "person/leaderboard"
            else:
                testUrl = testName
            if self.startdate is None or self.enddate is None and testUrl == "person/leaderboard":
                print "Leaderboard requests require start/enddate arguments"
                sys.exit()
            url += testUrl+"?format=json&api_key="+self.api
            if self.startdate is not None and self.enddate is not None:
                url += "&start_date="+self.formatDate(self.startdate)+"&end_date="+self.formatDate(self.enddate)
            objectData = self.getData(url)
            if test == 0:
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        sys.exit()
                    if not isinstance(object["down_votes"], int):
                        print "downvote not integer: "+str(object)
                        sys.exit()
                    if not isinstance(object["up_votes"], int):
                        print "upvote not integer: "+str(object)
                        sys.exit()
                    if not isinstance(object["trade_id"], int):
                        print "trade_id not integer: "+str(object)
                        sys.exit()
                    if not isinstance(object["comment_text"], unicode):
                        print "comment_text not unicode: "+str(object)
                        sys.exit()
