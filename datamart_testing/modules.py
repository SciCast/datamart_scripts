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
        @param test: test suite to run. If no argument, it will run whatever is set as self.test
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
            if self.startdate is None or self.enddate is None:
                if testUrl == "person/leaderboard":
                    print "Leaderboard requests require start/enddate arguments"
                    sys.exit()
            url += testUrl+"?format=json&api_key="+self.api
            if self.startdate is not None and self.enddate is not None:
                url += "&start_date="+self.formatDate(self.startdate)+"&end_date="+\
                       self.formatDate(self.enddate)
            objectData = self.getData(url)
            if test == 0: #comment sanity test
                #{"down_votes": 0, "up_votes": 0, "trade_id": null, "comment_text": "Current depth is already 1.5\", with a cold front coming in next week.", "user_id": 36, "is_alert": false, "created_at": "2013-12-04T10:45:46", "comment_id": 4, "parent_comment_id": null, "question_id": 51}
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        return False
                    if not isinstance(object["down_votes"], int):
                        print "downvote not integer: "+str(object)
                        return False
                    if not isinstance(object["up_votes"], int):
                        print "upvote not integer: "+str(object)
                        return False
                    if not isinstance(object["trade_id"], int) and object["trade_id"] is not None:
                        print "trade_id not integer or None: "+str(object)
                        return False
                    if not isinstance(object["comment_text"], unicode):
                        print "comment_text not unicode: "+str(object)
                        return False
                    if not isinstance(object["created_at"], datetime.datetime) \
                            and not isinstance(object["created_at"], unicode):
                        print "created_at not datetime or unicode: "+str(object)
                        return False
                    if not isinstance(object["parent_comment_id"], int) and object["parent_comment_id"] \
                            is not None:
                        print "parent_comment_id not integer or None: "+str(object)
                        return False
                    if not isinstance(object["question_id"], int):
                        print "question_id not integer: "+str(object)
                        return False
                    if not isinstance(object["is_alert"], bool) and not isinstance(object["is_alert"], int) \
                            and not isinstance(object["is_alert"], unicode):
                        print "is_alert not valid: "+str(object)
                        return False
                return True
            elif test == 1: #person sanity test
                #{"username": "daggre_admin", "interests": null, "user_id": 1, "created_at": "2013-11-17T10:37:23", "is_active": true, "default_trade_preference": null, "about_me": null, "referral_id": null, "groups": "QuestionAdmin,Study 2.1A,Admin,User,SuperAdmin,UserAdmin,Internal,BadgesAdmin,RolesAdmin", "num_trades": 30, "opt_out_email": null}
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        return False
                    if not isinstance(object["user_id"], int):
                        print "user_id not integer: "+str(object)
                        return False
                    if not isinstance(object["num_trades"], int):
                        print "num_trades not integer: "+str(object)
                        return False
                    if not isinstance(object["referral_id"], unicode) and object["referral_id"] is not None:
                        print "referral_id not unicode or None: "+str(object)
                        return False
                    if not isinstance(object["username"], unicode):
                        print "username not unicode: "+str(object)
                        return False
                    if not isinstance(object["groups"], unicode):
                        print "groups not unicode: "+str(object)
                        return False
                    if not isinstance(object["opt_out_email"], int) and object["opt_out_email"] is not None:
                        print "opt_out_email not integer or None: "+str(object)
                        return False
                    if not isinstance(object["interests"], unicode) and object["interests"] is not None:
                        print "interests not unicode or None: "+str(object)
                        return False
                    if not isinstance(object["default_trade_preference"], int) \
                            and object["default_trade_preference"] is not None:
                        print "default_trade_preference not int: "+str(object)
                        return False
                    if not isinstance(object["created_at"], datetime.datetime) \
                            and not isinstance(object["created_at"], unicode):
                        print "created_at not datetime or unicode: "+str(object)
                        return False
                    if not isinstance(object["about_me"], unicode) and object["about_me"] is not None:
                        print "about_me not unicode: "+str(object)
                        return False
                    if not isinstance(object["is_active"], bool) \
                            and not isinstance(object["is_alert"], int) and not isinstance(object["is_alert"], unicode):
                        print "is_active not valid: "+str(object)
                        return False
                return True
            elif test == 2:
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        return False
                    if not isinstance(object["max_score"], int) and object["max_score"] is not None:
                        print "max_score not integer: "+str(object)
                        return False
                    if not isinstance(object["user_id"], int):
                        print "user_id not integer: "+str(object)
                        return False
                    if not isinstance(object["sampled_at"], datetime.datetime) \
                            and not isinstance(object["sampled_at"], unicode):
                        print "sampled_at not datetime or unicode: "+str(object)
                        return False
                return True
            elif test == 3:
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        return False
                    if not isinstance(object["is_visible"], bool) \
                            and not isinstance(object["is_visible"], unicode):
                        print "is_visible invalid: "+str(object)
                        return False
                    if not isinstance(object["resolution_index"], float) \
                            and object["resolution_index"] is not None:
                        print "resolution_index invalid: "+str(object)
                        return False
                    if not isinstance(object["question_contributors"], unicode) \
                            and object["question_contributors"] is not None:
                        print "questin_contributors invalid: "+str(object)
                        return False
                    if not isinstance(object["keywords"], unicode) and object["keywords"] is not None:
                        print "keywords invalid: "+str(object)
                        return False
                    if not isinstance(object["relationships"], list):
                        return False
                    if not isinstance(object["question_text"], unicode):
                        print "question_text invalid: "+str(object)
                        return False
                    if not isinstance(object["priority"], int) and object["priority"] is not None:
                        print "priority invalid: "+str(object)
                        return False
                    if not isinstance(object["resolution_at"], datetime.datetime) \
                            and not isinstance(object["resolution_at"], unicode) and object["resolution_at"] is not None:
                        print "resolution_at invalid: "+str(object)
                        return False
                    if not isinstance(object["type"], unicode):
                        print "type invalid: "+str(object)
                        return False
                    if not isinstance(object["short_name"], unicode):
                        print "short_name invalid: "+str(object)
                        return False
                    if not isinstance(object["spark_id"], unicode) and object["spark_id"] is not None:
                        print "spark_id invalid: "+str(object)
                        return False
                    if not isinstance(object["resolution_value_array"], unicode) \
                            and not isinstance(object["resolution_value_array"], list) and object["resolution_value_array"] is not None:
                        print "resolution_value_array invalid: "+str(object)
                        return False
                    if not isinstance(object["groups"], unicode):
                        print "groups invalid: "+str(object)
                        return False
                    if not isinstance(object["last_traded_at"], datetime.datetime) \
                            and not isinstance(object["last_traded_at"], unicode) and object["last_traded_at"] is not None:
                        print "last_traded_at invalid: "+str(object)
                        return False
                    if not isinstance(object["categories"], unicode) and object["categories"] is not None:
                        print "categories invalid: "+str(object)
                        return False
                    if not isinstance(object["question_kind"], int) and object["question_kind"] is not None:
                        print "question_kind invalid: "+str(object)
                        return False
                    if not isinstance(object["name"], unicode):
                        print "name invalid: "+str(object)
                        return False
                    if not isinstance(object["is_locked"], bool) and not isinstance(object["is_locked"], unicode):
                        print "is_locked invalid: "+str(object)
                        return False
                    if not isinstance(object["created_at"], datetime.datetime) and not isinstance(object["created_at"], unicode):
                        print "created_at invalid: "+str(object)
                        return False
                    if not isinstance(object["choices"], list):
                        print "choices invalid: "+str(object)
                        return False
                    if not isinstance(object["pending_until"], datetime.datetime) and not isinstance(object["pending_until"], unicode) and object["pending_until"] is not None:
                        print "pending_until invalid: "+str(object)
                        return False
                    if not isinstance(object["challenge"], unicode) and object["challenge"] is not None:
                        print "challenge invalid: "+str(object)
                        return False
                    if not isinstance(object["question_id"], int):
                        print "question_id invalid: "+str(object)
                        return False
                return True