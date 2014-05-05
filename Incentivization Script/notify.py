# -*- coding: UTF-8 -*-
'''
Created on Mar 11, 2014
Incentivization Script Payment Function. Gets email addresses for users and sends payment notification

@author: ssmith
@copyright: 2014+
'''

import requests, json, sys, datetime, re, getopt, smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

userpassfile = open('userpass', 'r')
emailuserpass = userpassfile.readline().strip('\n').strip().split(':')
apiuserpass = userpassfile.readline().strip('\n').strip().split(':')
userpassfile.close()
allusers = None
configName = "config" # change this to change config file name
api = "scicast.org" #change this to change the market api variable

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

def getEmail(userid):
    for user in allusers:
        if user["id"] == userid:
            email = user["email"]
            if email is None or email == "":
                print "No email found for "+str(userid)
            return email
    return ""

def getData(targetUrl):
    """
    Does a call to targetUrl, parses result to json, returns the json

    @type targetUrl: String
    @param targetUrl: URL to pull data from, with options, etc
    @return: JSON object with results of query
    """
    print "Receiving: "+targetUrl
    s = requests.session()
    r=s.get("http://"+api+"/session/create?username="+apiuserpass[0]+"&password="+apiuserpass[1])
    o=None
    r = s.get(targetUrl)
    t = r.text
    r=s.get("http://"+api+"/session/destroy")
    #print t
    try:
        o = json.loads(t)
    except ValueError:
        print "Website return did not match expected format: "+t
        sys.exit()
    return o

def getFromFile(file):
        '''
        Gets list of previous winners, for keeping track of who's won
        @param opt: config file options
        @type opt: dict
        @return: information inside previous winners file or None if file doesn't exist
        '''
        filename = file+".json"
        if os.path.isfile(filename):
            json_data = open(filename)
            data = json.load(json_data)
            json_data.close()
            #print type(data)
        else:
            data = None
        return data

def sendEmail(userid,codes,userlist,opt):
    email = "ssmith@c4i.gmu.edu"
    name = "Scott Smith"
    fromemail = opt["from"]

    for user in userlist:
        if user["id"] == int(userid):
            print user
            email = user["email"]
            name = user["username"]
    fp = open(opt["html"], 'r')
    html_text = fp.read()
    fp.close()
    fp = open(opt["plain"], 'r')
    plain_text = fp.read()
    fp.close()

    html_text = re.sub('<<NAME>>',name,html_text)
    plain_text = re.sub('<<NAME>>',name,plain_text)

    img = open(opt["scicast"], 'rb')
    sci_logo = MIMEImage(img.read())
    img.close()
    img = open(opt["gmu"], 'rb')
    gmu_logo = MIMEImage(img.read())
    img.close()
    img = open(opt["amazon"], 'rb')
    ama_logo = MIMEImage(img.read())
    img.close()

    sci_logo.add_header('Content-ID', "@sci_logo")
    gmu_logo.add_header('Content-ID', "@gmu_logo")
    ama_logo.add_header('content-ID', "@ama_image")

    for code in codes:
        message_html = re.sub('<<CODE>>',code,html_text)
        message_plain = re.sub('<<CODE>>',code,plain_text)

        msgroot = MIMEMultipart('related')
        msgroot['Subject'] = "Test message to "+email
        msgroot['From'] = "ssmith@c4i.gmu.edu"
        msgroot['To'] = "ssmith@c4i.gmu.edu"#insert email here

        msgalternative = MIMEMultipart('alternative')
        msgroot.attach(msgalternative)

        part1 = MIMEText(message_html,'html')
        part2 = MIMEText(message_plain,'plain')

        msgroot.attach(sci_logo)
        msgroot.attach(gmu_logo)
        msgroot.attach(ama_logo)
        msgalternative.attach(part2)
        msgalternative.attach(part1)


        serverport = opt["server"]+":"+opt["port"]
        server = smtplib.SMTP(serverport)
        server.ehlo()
        server.starttls()
        server.login(emailuserpass[0],emailuserpass[1])
        print str(userid)+" "+code
        #server.sendmail(fromemail,["ssmith@c4i.gmu.edu"],msgroot.as_string())

def getCodes(number,opt,userid):
    codes = []
    f = open(opt["giftcards"],'r')
    lines = f.readlines()
    f.close()
    skip = False
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    out = open(opt["giftcards"],'w')
    log = getFromFile(opt["log"])
    if log is None:
        log = {}
    numwins = 0
    if  userid in log:
        user = log[userid]
        for key,value in user.iteritems():
            numwins += len(value)

    if numwins >= 23:
        print "User "+str(userid)+" has already won the maximum number of times."
        skip = True

    for i in range(0, len(lines)):
        #print len(lines[i].split(','))
        if skip:
            break
        else:
            if len(lines[i].split(',')) == 1:
                code = lines[i].strip('\n')
                codes.append(code)
                lines[i] = code+",USED\n"
                numwins += 1
                if userid in log:
                    if today_str in log[userid]:
                            log[userid][today_str].append(code)
                    else:
                            log[userid] = {today_str:[code]}
                else:
                    log[userid] = {today_str:[code]}
                #out.writelines(lines)
                number -= 1
                if numwins == 23:
                    print "User "+str(userid)+" has reached the maximum number of wins."
                    skip = True
                if number == 0:
                    skip = True
    writelog(log,opt)
    out.writelines(lines)
    out.close()
    return codes

def writelog(log,opt):
    '''
    Utility function to print activity levels, used for accumulation and some tracking
    @return: none
    '''
    filename = opt["log"]+".json"

    try:
        js = open(filename,'w')
        json.dump(log, js, sort_keys=True, indent=4)
        js.close()
        return True
    except ValueError:
        print "Error"

def main():
    '''
    Driver
    @param argv: Command line arguments
    @type argv: list
    @return: none
    '''

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    options = getConfig(configName)
    winners = getFromFile(options["winners"])
    all_users = getData("http://"+api+"/users/index")

    winlist = {}
    for userid,dates in winners.iteritems():
        if today_str in dates:
            winlist[userid] = dates[today_str]

    for userid,winnum in winlist.iteritems():
        codes = getCodes(winnum,options,userid)
        if len(codes) != winnum:
            print "Error: "+str(codes)+" for user "+str(userid)
            sys.exit(1)
        sendEmail(userid,codes,all_users,options)

if __name__ == '__main__': #driver function
    main()