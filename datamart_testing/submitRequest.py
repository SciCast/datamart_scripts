# -*- coding: UTF-8 -*-

'''
Created on Jan 13, 2014

@author: ssmith
Used to test datamart, both sanity and information verification checks
'''
import requests, csv, json, sys, datetime, re, modules, getopt

def removeNonAscii(s): return ''.join([i if ord(i) < 128 else ' ' for i in s])
def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

#person_url: http://scicast.org:8200/person/?format=json&api_key=
start = True
startDate = None
endDate = None
aggregate = False
filename = ""
test_list = ["comment","person","leaderboard","question","question_history","trade_history","all"]

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

def main(argv):
    """
    Main driver for program
    usage: submitRequest.py -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>] [-a, --aggregate] <aggregate_level> [-t, --test] <test type>
    If no params, will run all tests with no arguments
    """
    global startDate
    global endDate
    try:
      opts, args = getopt.getopt(argv,"hvit:s:e:a:",["test=","startdate=","enddate=","aggregate=","verify","ignore_errors"])
    except getopt.GetoptError:
        #If no arguments, run script assuming startdate == yesterday
        print 'No arguments detected; usage: submitRequest.py -h [-v, --verify] [-i, --ignore_errors] [-s, --startdate] <startdate> [-e, --enddate] <enddate>] [-a, --aggregate] <aggregate_level> [-t, --test] <test type>'
        sys.exit()
    #print opts
    startstring = ""
    endstring = ""
    aggregate_level = ""
    test_type = ""
    verify=False
    ignore=False
    aggregate_types = ["daily", "weekly", "monthly", "yearly"]
    for opt, arg in opts:
        if '-h' in args or opt == '-h': #Help documentation
            print 'submitRequest.py -h [-s, --startdate] <startdate> [-e, --enddate] <enddate>] [-a, --aggregate] <aggregate_level> [-t, --test] <test type>'
            sys.exit()
        elif opt in ("-s", "--startdate"):
            startstring = arg
        elif opt in ("-v", "--verify"):
            verify = True
        elif opt in ("-i", "--ignore_errors"):
            ignore = True
        elif opt in ("-e", "--enddate"):
            endstring = arg
        elif opt in ("-a", "--aggregate"):
            aggregate_level = arg
            if aggregate_level not in aggregate_types:
                print 'Acceptable aggregate levels: '+','.join(aggregate_types)
                sys.exit()
        elif opt in ("-t", "--test"):
            test_type = arg.lower().strip()

    if test_type:
        if test_type not in test_list:
            print "Test type not recognized. Test must match one of the following:"
            for test in test_list:
                print "- "+test
            sys.exit()
        else:
            #print test_type
            test = test_list.index(test_type)
    else:
        test = 6

    #convert strings into datetime objects
    if startstring:
        startDate = formatDate(startstring)
    else:
        if test == 6:
            startDate = datetime.datetime.now().strftime("%m-%d-%Y")

    if endstring:
        endDate = formatDate(endstring)
    else:
        if startstring:
            endDate = startDate
#["comment","person","leaderboard","question","question_history","trade_history"]
    if test != 6:
        testSuite = modules.suite(test, startDate, endDate, aggregate_level)
        if testSuite.sanity():
            print "Sanity test passed"
        if verify:
            testSuite = modules.suite(test,None, None, "")
            if testSuite.verification():
                print "Verification for "+test_list[test]+" completed successfully."
            else:
                print "Verification for "+test_list[test]+" failed."
                if not ignore:
                    sys.exit()
    else:
        for i in range(len(test_list)-1):
            if i == 0: #comment
                testSuite = modules.suite(i,None, None, "")
                if testSuite.sanity():
                    print "Non-date sanity check for "+test_list[i]+" completed successfully"
                else:
                    print "Non-date sanity check for "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                if verify:
                    if testSuite.verification():
                        print "Verification for "+test_list[i]+" completed successfully."
                    else:
                        print "Verification for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()
                testSuite.setstartdate(formatDate("01-01-2013"))
                testSuite.setenddate(formatDate(datetime.datetime.now().strftime("%m-%d-%Y")))
                if testSuite.sanity():
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" completed successfully"
                else:
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()

            elif i == 1: #person
                testSuite = modules.suite(i,None, None, "")
                if testSuite.sanity():
                    print "Non-date sanity check for "+test_list[i]+" completed successfully"
                else:
                    print "Non-date sanity check for "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                if verify:
                    if testSuite.verification():
                        print "Verification for "+test_list[i]+" completed successfully."
                    else:
                        print "Verification for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()
                testSuite.setstartdate(formatDate("01-01-2013"))
                testSuite.setenddate(formatDate(datetime.datetime.now().strftime("%m-%d-%Y")))
                if testSuite.sanity():
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" completed successfully"
                else:
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
            elif i == 2: #leaderboard
                testSuite = modules.suite(i,None, None, "")
                testSuite.setstartdate(formatDate("01-01-2013"))
                testSuite.setenddate(formatDate(datetime.datetime.now().strftime("%m-%d-%Y"))) #requires date, so we'll only do this test
                if testSuite.sanity():
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" completed successfully"
                else:
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
            elif i == 3: #question
                testSuite = modules.suite(i,None, None, "")
                if testSuite.sanity():
                    print "Non-date sanity check for "+test_list[i]+" completed successfully"
                else:
                    print "Non-date sanity check for "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                if verify:
                    if testSuite.verification():
                        print "Verification for "+test_list[i]+" completed successfully."
                    else:
                        print "Verification for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()
                testSuite.setstartdate(formatDate("01-01-2013"))
                testSuite.setenddate(formatDate(datetime.datetime.now().strftime("%m-%d-%Y")))
                if testSuite.sanity():
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" completed successfully"
                else:
                    print "Date sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
            elif i == 4: #question_history
                testSuite = modules.suite(i,None, None, "")
                if testSuite.sanity():
                    print "Non-date, non-aggregate sanity check for "+test_list[i]+" completed successfully"
                else:
                    print "Non-date, non-aggregate sanity check for "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                for level in aggregate_types:
                    testSuite.setaggregate(level)
                    if testSuite.sanity():
                        print "Non-date, "+level+" sanity check for "+test_list[i]+" completed successfully"
                    else:
                        print "Non-date, "+level+" sanity check for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()
                testSuite.setaggregate("")
                testSuite.setstartdate(formatDate("01-01-2013"))
                testSuite.setenddate(formatDate(datetime.datetime.now().strftime("%m-%d-%Y")))
                if testSuite.sanity():
                    print "Date, non-aggregate sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" completed successfully"
                else:
                    print "Date, non-aggregate sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                for level in aggregate_types:
                    testSuite.setaggregate(level)
                    if testSuite.sanity():
                        print "Date, "+level+" sanity check for "+test_list[i]+" completed successfully"
                    else:
                        print "Date, "+level+" sanity check for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()
            elif i == 5: #trade_history
                testSuite = modules.suite(i,None, None, "")
                if testSuite.sanity():
                    print "Non-date, non-aggregate sanity check for "+test_list[i]+" completed successfully"
                else:
                    print "Non-date, non-aggregate sanity check for "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                for level in aggregate_types:
                    testSuite.setaggregate(level)
                    if testSuite.sanity():
                        print "Non-date, "+level+" sanity check for "+test_list[i]+" completed successfully"
                    else:
                        print "Non-date, "+level+" sanity check for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()
                testSuite.setaggregate("")
                testSuite.setstartdate(formatDate("01-01-2013"))
                testSuite.setenddate(formatDate(datetime.datetime.now().strftime("%m-%d-%Y")))
                if testSuite.sanity():
                    print "Date, non-aggregate sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" completed successfully"
                else:
                    print "Date, non-aggregate sanity check for "+str(datetime.datetime.now())+" "+test_list[i]+" failed."
                    if not ignore:
                        sys.exit()
                for level in aggregate_types:
                    testSuite.setaggregate(level)
                    if testSuite.sanity():
                        print "Date, "+level+" sanity check for "+test_list[i]+" completed successfully"
                    else:
                        print "Date, "+level+" sanity check for "+test_list[i]+" failed."
                        if not ignore:
                            sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])