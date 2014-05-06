# -*- coding: UTF-8 -*-

'''
Created on Mar 24, 2014


@author: ssmith
'''

import sys, datetime, requests, json, numpy, re

class suite():
    def __init__(self, test=6, startdate=None, enddate=None, aggregate_level="", filename="config"):
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
        userpass = open('userpass', 'r').readline().strip('\n').split(':')
        self.username = userpass[0]
        self.password = userpass[1]
        self.testList = ["comment","person","leaderboard","question","question_history","trade_history"]

    def setstartdate(self, date):
        """
        @type date: datetime.datetime
        @param date: Date to save
        @return: None
        """
        self.startdate = date

    def setenddate(self, date):
        """
        @type date: datetime.datetime
        @param date: Date to save
        @return: None
        """
        self.enddate = date

    def setaggregate(self, aggregate):
        """
        @type aggregate: String
        @param aggregate: Aggregate level to set to
        @return: None
        """
        self.aggregate_level = aggregate

    def validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

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

    def getData(self,targetUrl,login=0):
        """
        Does a call to targetUrl, parses result to json, returns the json

        @type targetUrl: String
        @param targetUrl: URL to pull data from, with options, etc
        @return: JSON object with results of query
        """

        if self.options["debug"] == "1":
            print "Receiving: "+targetUrl
        s = requests.session()
        if login==1:
            r=s.get("http://"+self.options["url"]+"/session/create?username="+self.username+"&password="+self.password)
        if login==2:
            r=s.get("http://"+self.options["url"]+"/session/destroy")
            o=None
        else:
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

    def sanity(self):
        """
        Do sanity checks. This verifies several things:
            -No returned object contains more keys than any other object
            -No duplicate ID numbers
            -All value types are what is expected
                -eg value is not an integer if it is supposed to be a string
        Test indexes reference:
        ["comment","person","leaderboard","question","question_history","trade_history"]

        @param none: Chooses the test based on what was set when module created
        @return:
        """
        testUrl = ""
        test = self.test
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
        if self.aggregate_level is not "":
            url +="&aggregate_level="+self.aggregate_level
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
        elif test == 2: #leaderboard
            first = objectData[0]
            numKeys = len(first.keys())
            for object in objectData:
                if len(object.keys()) != numKeys:
                    print "Too many keys for "+str(object)
                    return False
                if not isinstance(object["max_score"], int) and object["max_score"] is not None \
                        and not isinstance(object["max_score"], float):
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
        elif test == 4:
            if self.aggregate_level is "":
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        return False
                    if not isinstance(object["probabilities"], unicode) and object["probabilities"] is not None:
                        print "probabilities not csv: "+str(object)
                        return False
                    if not isinstance(object["question_id"], int):
                        print "question_id not integer: "+str(object)
                        return False
                    if not isinstance(object["sampled_at"], datetime.datetime) \
                            and not isinstance(object["sampled_at"], unicode):
                        print "sampled_at not datetime or unicode: "+str(object)
                        return False
            elif self.aggregate_level == "yearly":
                data = objectData["data"]
                stats = objectData["stats"]
                nums = []
                for object in data:
                    year = object[0]
                    val = object[1]
                    if re.match('/^[0-9]{4}$/',year, re.UNICODE) is not None:
                        print "Key is not year "+str(year)+" "+str(val["unique_questions"])
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(year)+" "+str(val["unique_questions"])
                        return False
                    nums.append(val["unique_questions"])
                avg = numpy.average(nums, axis=0)
                if avg != stats["unique_questions"]["mean_statistics"]:
                    print "avg != "+str(avg)+" "+str(stats["unique_questions"]["mean_statistics"])
                    return False
                if numpy.std(nums, axis=0) != stats["unique_questions"]["stddev_statistics"]:
                    print "std: "+str(numpy.std(nums, axis=0))+" "+str(stats["unique_questions"]["stddev_statistics"])
                    #return False
            elif self.aggregate_level == "monthly":
                data = objectData["data"]
                stats = objectData["stats"]
                nums = []
                for object in data:
                    date = object[0]
                    val = object[1]
                    dateTest = date+"-01"
                    if not self.validate(dateTest):
                        print "Key was not valid date: "+str(date)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["unique_questions"])
                        return False
                    nums.append(val["unique_questions"])
                    avg = numpy.average(nums, axis=0)
                if avg != stats["unique_questions"]["mean_statistics"]:
                    print "avg != "+str(avg)+" "+str(stats["unique_questions"]["mean_statistics"])
                    return False
                if numpy.std(nums, axis=0) != stats["unique_questions"]["stddev_statistics"]:
                    print "std: "+str(numpy.std(nums, axis=0))+" "+str(stats["unique_questions"]["stddev_statistics"])
                    #return False
            elif self.aggregate_level == "weekly":
                data = objectData["data"]
                stats = objectData["stats"]
                nums = []
                for object in data:
                    date = object[0]
                    val = object[1]
                    keyList = date.split(":", 1)
                    if int(keyList[1]) > 52:
                        print "Too many weeks "+str(date)+" "+str(val)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["unique_questions"])
                        return False
                    nums.append(val["unique_questions"])
                    avg = numpy.average(nums, axis=0)
                if avg != stats["unique_questions"]["mean_statistics"]:
                    print "avg != "+str(avg)+" "+str(stats["unique_questions"]["mean_statistics"])
                    return False
                if numpy.std(nums, axis=0) != stats["unique_questions"]["stddev_statistics"]:
                    print "std: "+str(numpy.std(nums, axis=0))+" "+str(stats["unique_questions"]["stddev_statistics"])
                    #return False
            elif self.aggregate_level == "daily":
                data = objectData["data"]
                stats = objectData["stats"]
                nums = []
                for object in data:
                    date = object[0]
                    val = object[1]
                    if not self.validate(date):
                        print "Key was not valid date: "+str(date)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["unique_questions"])
                        return False
                    nums.append(val["unique_questions"])
                    avg = numpy.average(nums, axis=0)
                if avg != stats["unique_questions"]["mean_statistics"]:
                    print "avg != "+str(avg)+" "+str(stats["unique_questions"]["mean_statistics"])
                    return False
                if numpy.std(nums, axis=0) != stats["unique_questions"]["stddev_statistics"]:
                    print float(stats["unique_questions"]["stddev_statistics"]) == numpy.std(nums, axis=0).item()
                    print "std:"+str(numpy.std(nums, axis=0))+" "+str(stats["unique_questions"]["stddev_statistics"])
                    #return False
            return True
        elif test == 5:
            if self.aggregate_level is "":
                first = objectData[0]
                numKeys = len(first.keys())
                for object in objectData:
                    if len(object.keys()) != numKeys:
                        print "Too many keys for "+str(object)
                        return False
                    if not isinstance(object["choice_index"], int):
                        print "choice_index invalid: "+str(object)
                        return False
                    if not isinstance(object["trade_id"], int):
                        print "trade_id invalid: "+str(object)
                        return False
                    if not isinstance(object["old_value_list"], unicode):
                        print "old_value_list invalid: "+str(object)
                        return False
                    if not isinstance(object["new_value_list"], unicode):
                        print "new_value_list invalid: "+str(object)
                        return False
                    if not isinstance(object["assets_per_option"], unicode) and not isinstance(object["assets_per_option"], list):
                        print "assets_per_option invalid: "+str(object)
                        return False
                    if not isinstance(object["trade_status"], int) and object["trade_status"] is not None:
                        print "trade_status invalid: "+str(object)
                        return False
                    if not isinstance(object["asset_resolution"], float) and object["asset_resolution"] is not None:
                        print "asset_resolution invalid: "+str(object)
                        return False
                    if not isinstance(object["user_id"], int):
                        print "user_id invalid: "+str(object)
                        return False
                    if not isinstance(object["traded_at"], datetime.datetime) \
                            and not isinstance(object["traded_at"], unicode):
                        print "traded_at invalid: "+str(object)
                        return False
                    if not isinstance(object["serialized_assumptions"], unicode) and object["serialized_assumptions"] is not None:
                        print "serialized_assumptions invalid: "+str(object)
                        return False
                    if not isinstance(object["question_id"], int):
                        print "question_id invalid: "+str(object)
                        return False
                    if not isinstance(object["updated_at"], datetime.datetime) \
                            and not isinstance(object["updated_at"], unicode):
                        print "updated_at invalid: "+str(object)
                        return False
            elif self.aggregate_level == "yearly":
                data = objectData["data"]
                stats = objectData["stats"]
                num_trades = []
                num_traders = []
                unique_questions = []
                for object in data:
                    year = object[0]
                    val = object[1]
                    if re.match('/^[0-9]{4}$/',year, re.UNICODE) is not None:
                        print "Key is not year "+str(year)+" "+str(val)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(year)+" "+str(val["unique_questions"])
                        return False
                    if not val["num_trades"] and re.match(r'/^[0-9]{4}$/',val["num_trades"], re.UNICODE) is not None:
                        print "value incorrect "+str(year)+" "+str(val["num_trades"])
                        return False
                    if not val["num_traders"] and re.match(r'/^[0-9]{4}$/',val["num_traders"], re.UNICODE) is not None:
                        print "value incorrect "+str(year)+" "+str(val["num_traders"])
                        return False
                    unique_questions.append(val["unique_questions"])
                    num_trades.append(val["num_trades"])
                    num_traders.append(val["num_traders"])
                numpy_data = {"num_trades":{"mean_statistics":numpy.average(num_trades, axis=0), "stddev_statistics": numpy.std(num_trades, axis=0)},
                        "num_traders":{"mean_statistics":numpy.average(num_traders, axis=0), "stddev_statistics": numpy.std(num_traders, axis=0)},
                        "unique_questions":{"mean_statistics":numpy.average(unique_questions, axis=0), "stddev_statistics": numpy.std(unique_questions, axis=0)}}
                for stat_type,stat_list in stats.iteritems():
                    for name,val in stat_list.iteritems():
                        #print str(numpy_data[stat_type][name])+" "+str(val)
                        if numpy_data[stat_type][name] != val:
                            print stat_type+" "+name+": "+str(stat_list)
                            return False
            elif self.aggregate_level == "monthly":
                data = objectData["data"]
                stats = objectData["stats"]
                num_trades = []
                num_traders = []
                unique_questions = []
                for object in data:
                    date = object[0]
                    val = object[1]
                    dateTest = date+"-01"
                    if not self.validate(dateTest):
                        print "Key was not valid date: "+str(date)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["unique_questions"])
                        return False
                    if not val["num_trades"] and re.match(r'/^[0-9]{4}$/',val["num_trades"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["num_trades"])
                        return False
                    if not val["num_traders"] and re.match(r'/^[0-9]{4}$/',val["num_traders"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["num_traders"])
                        return False
                    unique_questions.append(val["unique_questions"])
                    num_trades.append(val["num_trades"])
                    num_traders.append(val["num_traders"])
                numpy_data = {"num_trades":{"mean_statistics":numpy.average(num_trades, axis=0), "stddev_statistics": numpy.std(num_trades, axis=0)},
                        "num_traders":{"mean_statistics":numpy.average(num_traders, axis=0), "stddev_statistics": numpy.std(num_traders, axis=0)},
                        "unique_questions":{"mean_statistics":numpy.average(unique_questions, axis=0), "stddev_statistics": numpy.std(unique_questions, axis=0)}}
                for stat_type,stat_list in stats.iteritems():
                    for name,val in stat_list.iteritems():
                        #print str(numpy_data[stat_type][name])+" "+str(val)
                        if numpy_data[stat_type][name] != val:
                            print stat_type+" "+name+": "+str(stat_list)
                            return False
            elif self.aggregate_level == "weekly":
                data = objectData["data"]
                stats = objectData["stats"]
                num_trades = []
                num_traders = []
                unique_questions = []
                for object in data:
                    date = object[0]
                    val = object[1]
                    keyList = date.split(":", 1)
                    if int(keyList[1]) > 52:
                        print "Too many weeks "+str(date)+" "+str(val)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["unique_questions"])
                        return False
                    if not val["num_trades"] and re.match(r'/^[0-9]{4}$/',val["num_trades"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["num_trades"])
                        return False
                    if not val["num_traders"] and re.match(r'/^[0-9]{4}$/',val["num_traders"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["num_traders"])
                        return False
                    unique_questions.append(val["unique_questions"])
                    num_trades.append(val["num_trades"])
                    num_traders.append(val["num_traders"])
                numpy_data = {"num_trades":{"mean_statistics":numpy.average(num_trades, axis=0), "stddev_statistics": numpy.std(num_trades, axis=0)},
                        "num_traders":{"mean_statistics":numpy.average(num_traders, axis=0), "stddev_statistics": numpy.std(num_traders, axis=0)},
                        "unique_questions":{"mean_statistics":numpy.average(unique_questions, axis=0), "stddev_statistics": numpy.std(unique_questions, axis=0)}}
                for stat_type,stat_list in stats.iteritems():
                    for name,val in stat_list.iteritems():
                        #print str(numpy_data[stat_type][name])+" "+str(val)
                        if numpy_data[stat_type][name] != val:
                            print stat_type+" "+name+": "+str(stat_list)
                            print str(numpy_data[stat_type][name])+" "+str(val)
                            return False
            elif self.aggregate_level == "daily":
                data = objectData["data"]
                stats = objectData["stats"]
                num_trades = []
                num_traders = []
                unique_questions = []
                for object in data:
                    date = object[0]
                    val = object[1]
                    if not self.validate(date):
                        print "Key was not valid date: "+str(date)
                        return False
                    if not val["unique_questions"] and re.match(r'/^[0-9]{4}$/',val["unique_questions"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["unique_questions"])
                        return False
                    if not val["num_trades"] and re.match(r'/^[0-9]{4}$/',val["num_trades"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["num_trades"])
                        return False
                    if not val["num_traders"] and re.match(r'/^[0-9]{4}$/',val["num_traders"], re.UNICODE) is not None:
                        print "value incorrect "+str(date)+" "+str(val["num_traders"])
                        return False
                    unique_questions.append(val["unique_questions"])
                    num_trades.append(val["num_trades"])
                    num_traders.append(val["num_traders"])
                numpy_data = {"num_trades":{"mean_statistics":numpy.average(num_trades, axis=0), "stddev_statistics": numpy.std(num_trades, axis=0)},
                        "num_traders":{"mean_statistics":numpy.average(num_traders, axis=0), "stddev_statistics": numpy.std(num_traders, axis=0)},
                        "unique_questions":{"mean_statistics":numpy.average(unique_questions, axis=0), "stddev_statistics": numpy.std(unique_questions, axis=0)}}
                for stat_type,stat_list in stats.iteritems():
                    for name,val in stat_list.iteritems():
                        #print str(numpy_data[stat_type][name])+" "+str(val)
                        if numpy_data[stat_type][name] != val:
                            print stat_type+" "+name+": "+str(stat_list)
                            print str(numpy_data[stat_type][name])+" "+str(val)
                            return False
            return True

    def verification(self):
        """
        Do verification checks. This verifies that information is passed correctly from market to datamart
        Test indexes reference:
        ["comment","person","leaderboard","question","question_history","trade_history"]

        @param none: Chooses the test based on what was set when module created
        @return: none
        """

        testUrl = ""
        test = self.test
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
        if self.aggregate_level is not "":
            url +="&aggregate_level="+self.aggregate_level
        datamartData = self.getData(url)
        dict = {}
        if test == 0: #comment
            for object in datamartData:
                dict[object["comment_id"]] = object
            url = "http://"+self.options["url"]+"/comments/index"
            marketData = self.getData(url,1)
            self.getData("",2)
            for comment in marketData:
                if comment["comment_id"] is None:
                    continue
                datamart_comment = dict[comment["comment_id"]]
                for key,val in comment.iteritems():
                    if val != datamart_comment[key]:
                        print "Potential issue: "+str(key)+" "+str(val)+" mismatch for comment_id "+str(comment["comment_id"])
                        return False
        if test == 1: #person
            for object in datamartData:
                dict[object["user_id"]] = object
            url = "http://"+self.options["url"]+"/users/index"
            marketData = self.getData(url,1)
            self.getData("",2)
            invalid_keys = []
            for user in marketData:
                if user["id"] is None:
                    continue
                if user["id"] not in dict:
                    print "Potential issue: user id "+str(user["id"])+" not found in datamart"
                    continue
                datamart_user = dict[user["id"]]
                for key,val in user.iteritems():
                    if key in datamart_user:
                        if val != datamart_user[key]:
                            print "Potential issue: "+str(key)+" "+str(val)+" mismatch for user_id "+str(user["id"])
                            #return False
                    elif key == "roles":
                        for role_info in val:
                            #print role_info["name"]+" "+datamart_user["groups"]
                            if role_info["name"] not in datamart_user["groups"]:
                                print "Potential issue: "+role_info["name"]+" not in group list for "+str(user["id"])

                    else:
                        if key not in invalid_keys:
                            print "Potential issue: "+str(key)+" not in datamart"
                            invalid_keys.append(key)
        if test == 3: #question
            for object in datamartData:
                dict[object["question_id"]] = object
            url = "http://"+self.options["url"]+"/questions/index"
            marketData = self.getData(url,1)
            self.getData("",2)
            invalid_keys = []
            serialized_issues = []
            for question_dict in marketData:
                question = question_dict["question"]
                question_categories = question_dict["question_categories"]
                #print question
                if question["id"] is None:
                    continue
                if question["id"] not in dict:
                    if question["created_at"].split("T")[0] != datetime.datetime.now().strftime("%Y-%m-%d"):
                        print "Potential issue: question id "+str(question["id"])+" not found in datamart"
                    continue
                if question["is_ordered"] == True and question["serialized_model"] is not None:
                    if len(question["serialized_model"]["range"]) == 0 and len(question["serialized_model"]["bins"]) == 0:
                        #print "Potential issue: question id "+str(question["id"])+" is ordered but serialized_model is null"
                        serialized_issues.append(question["id"])
                datamart_question = dict[question["id"]]
                for key,val in question.iteritems():
                    if key in datamart_question:
                        if key == "created_at":
                            date_part = val.split("T")
                            if date_part[0] != datamart_question[key].split("T")[0]:
                                #print "Potential issue: "+str(key)+" "+str(val)+" mismatch for question_id "+str(question["id"])
                                print date_part[0]+" "+datamart_question[key].split("T")[0]
                        else:
                            if val != datamart_question[key]:
                                print "Potential issue: "+str(key)+" "+str(val)+" mismatch for question_id "+str(question["id"])
                                #return False
                    elif key == "categories":
                        for cat_info in question_categories:
                            if cat_info["name"] not in val:
                                print "Potential issue: "+cat_info["name"]+" not in group list for "+str(question["id"])
                    else:
                        if key not in invalid_keys:
                            print "Potential issue: "+str(key)+" not in datamart"
                            invalid_keys.append(key)
            print "Questions where ordered is true and serialized_assumptions is null: "+str(sorted(serialized_issues))
        return True

