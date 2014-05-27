# -*- coding: UTF-8 -*-
'''
Created on Mar 11, 2014
Incentivization Script Payment Function. Gets email addresses for users and sends payment notification

@author: ssmith
@copyright: 2014+
'''

import requests, json, sys, datetime, re, getopt, smtplib, os, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

userpassfile = open('userpass', 'r')
emailuserpass = userpassfile.readline().strip('\n').strip().split(':')
apiuserpass = userpassfile.readline().strip('\n').strip().split(':')
userpassfile.close()
allusers = None
configName = "config"  # change this to change config file name
api = "scicast.org"  #change this to change the market api variable
dayName = ""


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
                print "No email found for " + str(userid)
            return email
    return ""


def getData(targetUrl):
    """
    Does a call to targetUrl, parses result to json, returns the json

    @type targetUrl: String
    @param targetUrl: URL to pull data from, with options, etc
    @return: JSON object with results of query
    """
    print "Receiving: " + targetUrl
    s = requests.session()
    r = s.get("http://" + api + "/session/create?username=" + apiuserpass[0] + "&password=" + apiuserpass[1])
    o = None
    r = s.get(targetUrl)
    t = r.text
    r = s.get("http://" + api + "/session/destroy")
    #print t
    try:
        o = json.loads(t)
    except ValueError:
        print "Website return did not match expected format: " + t
        sys.exit()
    return o


def getFromFile(file):
    '''
    Gets list of previous winners, for keeping track of who's won
    @param opt: config file options
    @type opt: dict
    @return: information inside previous winners file or None if file doesn't exist
    '''
    filename = file + ".json"
    if os.path.isfile(filename):
        json_data = open(filename)
        data = json.load(json_data)
        json_data.close()
        #print type(data)
    else:
        data = None
    return data


def sendCodeEmail(userid, codes, userlist, opt):
    global dayName
    email = "ssmith@c4i.gmu.edu"
    name = "Scott Smith"
    fromemail = opt["from"]

    for user in userlist:
        if user["id"] == int(userid):
            #print user
            email = user["email"]
            name = user["username"]
    fp = open(opt["codehtml"], 'r')
    html_text = fp.read()
    fp.close()
    fp = open(opt["codeplain"], 'r')
    plain_text = fp.read()
    fp.close()

    html_text = re.sub('<<NAME>>', name, html_text)
    plain_text = re.sub('<<NAME>>', name, plain_text)
    html_text = re.sub('<<DAY>>', dayName, html_text)
    plain_text = re.sub('<<DAY>>', dayName, plain_text)

    img = open(opt["scicast"], 'rb')
    sci_logo = MIMEImage(img.read())
    img.close()
    img = open(opt["amazon"], 'rb')
    ama_logo = MIMEImage(img.read())
    img.close()

    sci_logo.add_header('Content-ID', "@sci_logo")
    ama_logo.add_header('content-ID', "@ama_image")

    totalcodes = len(codes)
    for code in codes:
        currentcode = codes.index(code) + 1
        message_html = re.sub('<<CODE>>', code, html_text)
        message_plain = re.sub('<<CODE>>', code, plain_text)

        msgroot = MIMEMultipart('related')
        subjectText = "Amazon Gift Code from Scicast.org"
        if totalcodes > 1:
            subjectText += " code " + str(currentcode) + " of " + str(totalcodes)
        msgroot['Subject'] = subjectText
        msgroot['From'] = "Awards@scicast.org"
        msgroot['Reply-to'] = "Awards@scicast.org"
        msgroot['To'] = "ssmith@c4i.gmu.edu"  #insert email here

        msgalternative = MIMEMultipart('alternative')
        msgroot.attach(msgalternative)

        part1 = MIMEText(message_html, 'html')
        part2 = MIMEText(message_plain, 'plain')

        msgroot.attach(sci_logo)
        msgroot.attach(ama_logo)
        msgalternative.attach(part2)
        msgalternative.attach(part1)

        serverport = opt["server"] + ":" + opt["port"]
        server = smtplib.SMTP(serverport)
        server.ehlo()
        server.starttls()
        server.login(emailuserpass[0], emailuserpass[1])
        print str(userid) + " " + code
        server.sendmail("Awards@scicast.org", ["Awards@scicast.org"], msgroot.as_string())
        server.quit()


def sendThanksEmail(userid, active_list, userlist, opt):
    global dayName
    email = "ssmith@c4i.gmu.edu"
    name = "user"
    htmllist = opt["thankhtml"].split(',')
    plainlist = opt["thankplain"].split(',')
    bodytext = random.randint(0, len(htmllist) - 1)
    print active_list
    trades = 0
    comments = 0
    activity = ""
    if "trades" in active_list:
        trades = len(active_list["trades"])
    if "comments" in active_list:
        comments = len(active_list["comments"])
    if trades > 0:
        if trades == 1:
            activity = str(trades) + " trade"
        else:
            activity = str(trades) + " trades"
        if comments > 0:
            activity += " and "
            if comments == 1:
                activity += str(comments) + " comment"
            else:
                activity += str(comments) + " comments"
    else:
        if comments == 1:
            activity = str(comments) + " comment"
        else:
            activity = str(comments) + " comments"

    fromemail = opt["from"]

    for user in userlist:
        if user["id"] == int(userid):
            #print user
            email = user["email"]
            name = user["username"]
    fp = open(htmllist[bodytext], 'r')
    html_text = fp.read().decode('utf-8')
    fp.close()
    fp = open(plainlist[bodytext], 'r')
    plain_text = fp.read().decode('utf-8')
    fp.close()

    html_text = re.sub('<<NAME>>', name, html_text)
    plain_text = re.sub('<<NAME>>', name, plain_text)
    html_text = re.sub('<<ACTIVITY>>', activity, html_text)
    plain_text = re.sub('<<ACTIVITY>>', activity, plain_text)
    html_text = re.sub('<<DAY>>', dayName, html_text)
    plain_text = re.sub('<<DAY>>', dayName, plain_text)

    img = open(opt["scicast"], 'rb')
    sci_logo = MIMEImage(img.read())
    img.close()

    sci_logo.add_header('Content-ID', "@sci_logo")

    msgroot = MIMEMultipart('related')
    msgroot['Subject'] = "Thank you from the SciCast team"
    msgroot['From'] = "Awards@scicast.org"
    msgroot['Reply-to'] = "Awards@scicast.org"
    msgroot['To'] = "Awards@scicast.org"  #insert email here

    msgalternative = MIMEMultipart('alternative')
    msgroot.attach(msgalternative)

    part1 = MIMEText(html_text, 'html')
    part2 = MIMEText(plain_text, 'plain')

    msgroot.attach(sci_logo)
    msgalternative.attach(part2)
    msgalternative.attach(part1)

    serverport = opt["server"] + ":" + opt["port"]
    server = smtplib.SMTP(serverport)
    server.ehlo()
    server.starttls()
    server.login(emailuserpass[0], emailuserpass[1])
    server.sendmail("Awards@scicast.org", ["Awards@scicast.org"], msgroot.as_string())
    server.quit()


def sendSwagEmail(userid, swagnum, winnum, userlist, opt):
    global dayName
    email = "ssmith@c4i.gmu.edu"
    name = "Scott Smith"
    fromemail = opt["from"]
    fail = False
    badge = ""
    congrats = ""
    html_list = ""
    plain_list = ""

    for user in userlist:
        if user["id"] == int(userid):
            #print user
            email = user["email"]
            name = user["username"]
    fp = open(opt["swaghtml"], 'r')
    html_text = fp.read()
    fp.close()
    fp = open(opt["swagplain"], 'r')
    plain_text = fp.read()
    fp.close()

    html_text = re.sub('<<NAME>>', name, html_text)
    plain_text = re.sub('<<NAME>>', name, plain_text)
    html_text = re.sub('<<DAY>>', dayName, html_text)
    plain_text = re.sub('<<DAY>>', dayName, plain_text)

    img = open(opt["scicast"], 'rb')
    sci_logo = MIMEImage(img.read())
    img.close()

    sci_logo.add_header('Content-ID', "@sci_logo")

    if winnum == 1:
        todaytext = str(winnum) + " merit"
    else:
        todaytext = str(winnum) + " merits"

    html_text = re.sub("<<NUMBER>>", str(swagnum), html_text)
    plain_text = re.sub("<<NUMBER>>", str(swagnum), plain_text)
    html_text = re.sub("<<TODAY>>", str(todaytext), html_text)
    plain_text = re.sub("<<TODAY>>", str(todaytext), plain_text)

    startswag = swagnum - winnum
    nextLevel = 0
    for i in [3, 7, 15, 31, 63]:
        if i - swagnum > 0:
            nextLevel = i - swagnum
            break
    if nextLevel != 0:
        nextText = "Only " + str(nextLevel) + " merit "
        if nextLevel == 1:
            nextText += "point"
        else:
            nextText += "points"
        nextText += " until you advance to the next merit level!"
        html_text = re.sub("<<NEXT>>", nextText, html_text)
        plain_text = re.sub("<<NEXT>>", nextText, plain_text)
    else:
        html_text = re.sub("<<NEXT>>", "", html_text)
        plain_text = re.sub("<<NEXT>>", "", plain_text)

    if swagnum == 0:
        fail = True
    elif swagnum == 1 or swagnum == 2:
        badge = "a Helium"  #1
    elif swagnum > 2 and swagnum < 7:
        badge = "a Neon"  #2
    elif swagnum >= 7 and swagnum < 15:
        badge = "an Argon"  #4
    elif swagnum >= 15 and swagnum < 31:
        badge = "a Krypton"  #8
    elif swagnum >= 31 and swagnum < 63:
        badge = "a Xenon"  #16
    elif swagnum >= 63:
        badge = "a Radon"  #32
    else:
        print "Uh-oh: " + str(swagnum) + " " + str(userid)
        fail = True

    badges_list = []
    ids_list = []
    for i in range(0, winnum):
        if startswag + i == 0:
            badges_list.append("Helium")
            ids_list.append(opt["he"])
        elif startswag + i == 2:
            badges_list.append("Neon")
            ids_list.append(opt["ne"])
        elif startswag + i == 6:
            badges_list.append("Argon")
            ids_list.append(opt["ar"])
        elif startswag + i == 15:
            badges_list.append("Krypton")
            ids_list.append(opt["kr"])
        elif startswag + i == 31:
            badges_list.append("Xenon")
            ids_list.append(opt["xe"])
        elif startswag + i == 63:
            badges_list.append("Radon")
            ids_list.append(opt["rn"])

    badge_images = []
    if len(badges_list) == 1:
        if badges_list[0] == "Helium":
            congrats = "You've earned your first ever merit badge! "
        else:
            congrats = "You've upgraded to a new merit level! "
        congrats += "The following badge has been added to your profile page:"
        html_list += "<br /><ul>"
        plain_list += "\n"
        for badge_name in badges_list:
            html_list += "<li><img src=\"cid:@" + opt[
                badge_name.lower()] + "\" width=\"30\" height=\"30\"/> " + badge_name + "</li>"
            plain_list += "- " + badge_name + "\n"
            img = open(opt[badge_name.lower()], 'rb')
            badge_image = MIMEImage(img.read())
            img.close()
            badge_image.add_header('Content-ID', "@" + opt[badge_name.lower()])
            badge_images.append(badge_image)
        html_list += "</ul>"
    elif len(badges_list) > 1:
        if "Helium" in badges_list:
            congrats = "You've not only earned your first ever merit badge, you've earned " + str(
                len(badges_list)) + "! "
        else:
            congrats = "You've upgraded " + str(len(badges_list)) + " badge levels! "
        congrats += "The following badges have been added to your profile page:"
        html_list += "<br /><ul>"
        plain_list += "\n"
        for badge_name in badges_list:
            html_list += "<li><img src=\"cid:@" + opt[
                badge_name.lower()] + "\" width=\"30\" height=\"30\"/> " + badge_name + "</li>"
            plain_list += "- " + badge_name + "\n"
            img = open(opt[badge_name.lower()], 'rb')
            badge_image = MIMEImage(img.read())
            img.close()
            badge_image.add_header('Content-ID', "@" + opt[badge_name.lower()])
            badge_images.append(badge_image)
        html_list += "</ul>"

    html_congrats = congrats + html_list
    plain_congrats = congrats + plain_list

    #TODO: add badges with API calls

    #applyBadges(userid,opt,ids_list)

    html_text = re.sub("<<CONGRATS>>", html_congrats, html_text)
    plain_text = re.sub("<<CONGRATS>>", plain_congrats, plain_text)

    html_text = re.sub("<<ELEMENT>>", badge, html_text)
    plain_text = re.sub("<<ELEMENT>>", badge, plain_text)

    msgroot = MIMEMultipart('related')
    msgroot['Subject'] = "You've won merits on SciCast.org! TEST FOR 5/27/14"
    msgroot['From'] = "Awards@scicast.org"
    msgroot['Reply-to'] = "Awards@scicast.org"
    msgroot['To'] = "Awards@scicast.org"  #insert email here

    msgalternative = MIMEMultipart('alternative')
    msgroot.attach(msgalternative)

    part1 = MIMEText(html_text.encode('utf8'), 'html')
    part2 = MIMEText(plain_text.encode('utf8'), 'plain')

    msgroot.attach(sci_logo)
    for i in badge_images:
        msgroot.attach(i)
    msgalternative.attach(part2)
    msgalternative.attach(part1)

    serverport = opt["server"] + ":" + opt["port"]
    server = smtplib.SMTP(serverport)
    server.ehlo()
    server.starttls()
    server.login(emailuserpass[0], emailuserpass[1])
    if not fail:
        server.sendmail("Awards@scicast.org", ["Awards@scicast.org"], msgroot.as_string())
        server.quit()


def applyBadges(userid, opt, ids_list):
    """
    Does a call to targetUrl, parses result to json, returns the json

    @type targetUrl: String
    @param targetUrl: URL to pull data from, with options, etc
    @return: JSON object with results of query
    """
    s = requests.session()
    r = s.get("http://test." + api + "/session/create?username=" + apiuserpass[0] + "&password=" + apiuserpass[1])
    o = None
    for badge in ids_list:
        r = s.get("http://test." + api + "/user_badges/create?user_id=" + str(userid) + "&user_badge_id=" + str(badge))
        print "Applied badge " + str(badge) + " to user " + str(userid)
        #print "http://test."+api+"/user_badges/create?user_id="+str(userid)+"&user_badge_id="+str(badge)
        #r = s.get(targetUrl)
        #t = r.text
        #r=s.get("http://"+api+"/session/destroy")
        #print t
        #try:
        #    o = json.loads(t)
        #except ValueError:
        #    print "Website return did not match expected format: "+t
        #   sys.exit()
        #return o


def getCodes(number, opt, userid, typeV):
    skip = False
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    log = getFromFile(opt["log"])
    if log is None:
        log = {}
    numwins = 0
    numwinsToday = 0
    numswag = 0
    num2 = number
    limit = int(opt["daily"])
    codes = []

    if userid in log:
        user = log[userid]
        for key, value in user.iteritems():
            if "amazon" in value:
                numwins += len(value["amazon"])
            if "badge" in value:
                numswag += value["badge"]
    if numwins >= 23:
        print "User " + str(userid) + " has already won the maximum number of times."
        skip = True

    if "code" in typeV:
        f = open(opt["giftcards"], 'r')
        lines = f.readlines()
        f.close()
        for i in range(0, len(lines)):
            #print lines[i]
            if skip:
                if number > 0:
                    num2 += 1
                    number -= 1
                else:
                    numwins += numwinsToday
                    break
            else:
                if len(lines[i].split(',')) == 1:
                    code = lines[i].strip('\n')
                    codes.append(code)
                    lines[i] = code + ",USED\n"
                    out = open(opt["giftcards"], 'w')
                    out.writelines(lines)
                    out.close()
                    numwinsToday += 1
                    if userid in log:
                        if today_str in log[userid]:
                            if "amazon" in log[userid][today_str]:
                                log[userid][today_str]["amazon"].append(code)
                            else:
                                log[userid][today_str]["amazon"] = [code]
                        else:
                            log[userid][today_str] = {"amazon": [code]}
                    else:
                        log[userid] = {today_str: {"amazon": [code]}}
                    #out.writelines(lines)
                    number -= 1
                    if numwins == 23 or numwinsToday >= limit:
                        print "User " + str(userid) + " has reached the maximum number of wins."
                        skip = True
                    if number == 0:
                        skip = True
    if "swag" in typeV:
        while num2 > 0:
            if userid in log:
                if today_str in log[userid]:
                    if "badge" in log[userid][today_str]:
                        log[userid][today_str]["badge"] += 1
                    else:
                        log[userid][today_str]["badge"] = 1
                else:
                    log[userid][today_str] = {"badge": 1}
            else:
                log[userid] = {today_str: {"badge": 1}}
            num2 -= 1
        log[userid][today_str]["badge"] += numswag
    if len(typeV) == 1 and "thank" in typeV:
        return [None, None]
    if "swag" in typeV:
        badgenum = log[userid][today_str]["badge"]
    else:
        badgenum = 0
    writelog(log, opt)
    return [codes, badgenum]


def writelog(log, opt):
    '''
    Utility function to print activity levels, used for accumulation and some tracking
    @return: none
    '''
    filename = opt["log"] + ".json"

    try:
        js = open(filename, 'w')
        json.dump(log, js, sort_keys=True, indent=4)
        js.close()
        return True
    except ValueError:
        print "Error"


def main(argv):
    '''
    Driver
    @param argv: Command line arguments
    @type argv: list
    @return: none
    '''
    global dayName
    typestring = ""
    dayString = ""

    send = True
    try:
        opts, args = getopt.getopt(argv, "ht:d:", ["type", "day"])
    except getopt.GetoptError:
        #If no arguments, run script assuming startdate == yesterday
        print 'No arguments detected; usage: notify.py -h [-t, --type] <type>  [-d --day] <day>'
        sys.exit()

    print opts
    for opt, arg in opts:
        if '-h' in args or opt == '-h':  #Help documentation
            print 'notify.py -h [-t, --type] <type> [-d --day] <day>'
            print '"Day" is a day of the week, one of the following'
            for day in ["monday,m,mon", "tuesday,t,tue", "wednesday,w,wed", "thursday,r,thurs", "friday,f,fri"]:
                print "- " + day
            sys.exit()
        elif opt in ("-t", "--types"):
            typestring += arg.lower() + ","
        elif opt in ("-d", "--day"):
            dayString = arg.lower()
        elif opt in ("-i", "--ignore"):
            send = False

    if dayString == "monday" or dayString == "m" or dayString == "mon":
        dayName = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m-%d-%Y')
    elif dayString == "tuesday" or dayString == "t" or dayString == "tues":
        dayName = "Super Tuesday"
    elif dayString == "wednesday" or dayString == "w" or dayString == "wed":
        dayName = "Badge Wednesday"
    elif dayString == "thursday" or dayString == "r" or dayString == "thurs":
        dayName = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m-%d-%Y')
    elif dayString == "friday" or dayString == "f" or dayString == "fri":
        dayName = "Fortune Friday"
    else:
        print "Day not recognized. Day must match one of the following:"
        for test in ["monday,m,mon", "tuesday,t,tue", "wednesday,w,wed", "thursday,r,thurs", "friday,f,fri"]:
            print "- " + test
        sys.exit()
    typestring = typestring[:-1]
    if typestring:
        for reward in typestring.split(','):
            if reward not in ["code", "swag", "thank"]:
                print "Incentive type not recognized. Type must match one of the following:"
                for test in ["code", "swag", "thank"]:
                    print "- " + test
                sys.exit()
    else:
        print "Incentive type is required. Type must match one or more of the following:"
        for test in ["code", "swag", "thank"]:
            print "- " + test
        sys.exit()
    typearray = typestring.split(',')
    if "swag" not in typearray:
        send = True

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    options = getConfig(configName)
    winners = getFromFile(options["winners"])
    all_users = getData("http://" + api + "/users/index?role=None&traded_since=None")

    winlist = {}
    for userid, dates in winners.iteritems():
        if today_str in dates:
            winlist[userid] = dates[today_str]

    print winlist
    #sys.exit(1)
    for userid, winnum in winlist.iteritems():
        print type(userid)
        numActivityWins = 0
        for typeV, ids in winnum.iteritems():
            numActivityWins += len(ids)
        returned = getCodes(numActivityWins, options, userid, typearray)
        codes = returned[0]
        badgenum = returned[1]
        if "code" in typearray and len(codes) < numActivityWins:
            numActivityWins += numActivityWins - len(codes)
        print badgenum
        #if codes and len(codes) != numActivityWins or len(codes) != 23 and "code" in typearray:
        #    print "Error: "+str(codes)+" for user "+str(userid)
        #    sys.exit(1)
        print "Sending mail to " + str(userid)
        if "code" in typearray:
            sendCodeEmail(userid, codes, all_users, options)
        if "swag" in typearray and send:
            sendSwagEmail(userid, badgenum, numActivityWins, all_users, options)
        if "thank" in typearray:
            sendThanksEmail(userid, winnum, all_users, options)


if __name__ == '__main__':  #driver function
    main(sys.argv[1:])
