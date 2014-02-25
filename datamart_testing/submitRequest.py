'''
Created on Jan 13, 2014


@author: ssmith
'''
import requests, csv, json, sys, datetime, re

def removeNonAscii(s): return ''.join([i if ord(i) < 128 else ' ' for i in s])
def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

#person_url: http://test.scicast.org:8200/person/?format=json&api_key=
api = open('api_key', 'r').readline().strip('\n')
url="http://test.scicast.org:8200/"
urlEnd="/?format=json&api_key="+api
start = True
startdate = datetime.datetime.now()
enddate = datetime.datetime.now()
aggregate = False
aggregateLevel = ""
filename = ""

if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.exit("Usage: python submitRequest.py type_of_request [start date, end date, aggregate level]")
  else:
    s = requests.session()
    targetUrl = url+sys.argv[1]+urlEnd
    filename = sys.argv[1]
    if len(sys.argv) > 2:
      for i in range(2, len(sys.argv)):
        if sys.argv[i].find("-") != -1:
          if start:
            targetUrl += "&start_date="+sys.argv[i]
            startdate = datetime.datetime.strptime(sys.argv[i]+" 00:00:00", "%m-%d-%Y %H:%M:%S")
            start = False
          else:
            targetUrl += "&end_date="+sys.argv[i]
            enddate = datetime.datetime.strptime(sys.argv[i]+" 23:59:59", "%m-%d-%Y %H:%M:%S")
        else:
          targetUrl += "&aggregate_level="+sys.argv[i]
          filename+="_"+sys.argv[i]
          aggregateLevel = sys.argv[i]
          aggregate = True
    print targetUrl
    #if targetUrl.find("-") != -1:
    #  sys.exit("Date threshold mapping is not working at the moment. Please try again without these parameters.")
    try:
      with open(filename+".json") as js:
        o = json.load(js)
      js.close()
      print "Data pulled from file"
    except IOError:
      print "Receiving: "+targetUrl
      r = s.get(targetUrl)
      t = r.text
      #print t
      try:
        o = json.loads(t)
      except ValueError:
        sys.exit("Website return did not match expected format")
      js = open(filename+".json",'w')
      json.dump(o, js, sort_keys=True, indent=4)
      js.close()
    keys = []

    if sys.argv[1] == "person":
      for person in o:
        keyCounter = 0
        for key,value in person.iteritems():
          if key not in keys:
            print "New key found: "+removeNonAscii(str(key))
            keys.append(removeNonAscii(str(key)))
            keyCounter += 1
            if keyCounter > 13:
              sys.exit("Too many keys!")
          if removeNonAscii(str(key)) == "interests":
            if value is not None:
              if not isinstance(value, unicode) and not isinstance(value, str):
                sys.exit("Bad value for "+removeNonAscii(str(value))+" "+str(type(value)))
          elif removeNonAscii(str(key)) == "uninvested_assets":
            if not isinstance(value, float):
              sys.exit("Bad value for "+removeNonAscii(str(value))+" "+str(type(value)))
          elif removeNonAscii(str(key)) == "username":
            print removeNonAscii(str(value))
            if not isinstance(value, unicode) and not isinstance(value, str) :
              sys.exit("Bad value for "+removeNonAscii(str(value))+" "+str(isinstance(value, unicode)))
          if not start:
            if removeNonAscii(str(key)) == "created_at":
              created = datetime.datetime.strptime(removeNonAscii(str(value)), "%Y-%m-%dT%H:%M:%S")
              if created < startdate or created > enddate:
                sys.exit("outside date bounds "+removeNonAscii(str(value)))
      print "Person verified sanity check"

    elif sys.argv[1] == "comment":
      for comment in o:
        keyCounter = 0
        for key,value in comment.iteritems():
          if key not in keys:
            print "New key found: "+removeNonAscii(str(key))
            keys.append(removeNonAscii(str(key)))
            keyCounter += 1
            if keyCounter > 10:
              sys.exit("Too many keys!")
          if removeNonAscii(str(key)) == "comment_Text":
            if not isinstance(value, unicode) and not isinstance(value, str):
              sys.exit("Bad value for "+removeNonAscii(str(value))+" "+str(type(value)))
          elif removeNonAscii(str(key)) == "question_id" or removeNonAscii(str(key)) == "user_id":
            if not isinstance(value, int):
              sys.exit("Bad value for "+removeNonAscii(str(key))+": "+removeNonAscii(str(value))+" "+str(type(value)))
          if not start:
            if removeNonAscii(str(key)) == "created_at":
              created = datetime.datetime.strptime(removeNonAscii(str(value)), "%Y-%m-%dT%H:%M:%S")
              if created < startdate or created > enddate:
                sys.exit("outside date bounds "+removeNonAscii(str(value)))
      print "Comments verified sanity check"

    elif sys.argv[1] == "question":
      questions = {}
      dupes = {}
      for question in o:
        keyCounter = 0
	#print question
	if question["question_id"] in questions.keys():
		sys.exit("Question ID already exists "+question["question_id"])
	elif question["short_name"] in questions.values():
		if question["short_name"] in dupes.keys():
			dupes[question["short_name"]].append(question["question_id"])
		else:
			dupes[question["short_name"]] = [question["question_id"]]
	else:
		questions[question["question_id"]] = question["short_name"]
		dupes[question["short_name"]] = [question["question_id"]]
        for key,value in question.iteritems():
          if key not in keys:
            print "New key found: "+removeNonAscii(str(key))
            keys.append(removeNonAscii(str(key)))
            keyCounter += 1
            if keyCounter > 22:
              sys.exit("Too many keys!")
          if value is not None:
            if removeNonAscii(str(key)) == "question_text" or  removeNonAscii(str(key)) == "name" or  removeNonAscii(str(key)) == "short_name":
              if not isinstance(value, unicode) and not isinstance(value, str):
                sys.exit("Bad value for "+removeNonAscii(str(value))+" "+str(type(value)))
            if removeNonAscii(str(key)) == "categories" or removeNonAscii(str(key)) == "choices" or removeNonAscii(str(key)) == "keywords":
              if not isinstance(value, unicode) and not isinstance(value, str):
                sys.exit("Bad value for "+removeNonAscii(str(value))+" "+str(type(value)))
            #TODO: Date threshold mapping
      remove = []
      for qid,qlist in dupes.iteritems():
	if len(qlist) == 1:
		remove.append(qid)
      for qid in remove:
	del dupes[qid]
      print dupes
      print "Questions verified sanity check"

    elif sys.argv[1] == "question_history":
      if aggregate:
        for aggregate in o["data"]:
          keyCounter = 0
          if aggregateLevel == "weekly":
            keyList = aggregate[0].split(":", 1)
            if int(keyList[1]) > 52:
              sys.exit("Too many weeks: "+str(keyList))
            for key,value in aggregate[1].iteritems():
              keyCounter += 1
              if keyCounter > 1:
                sys.exit("Too many keys: "+aggregate[1])
              if key != "unique_questions":
                sys.exit("Invalid key: "+key)
              if not isinstance(value, int):
                sys.exit("Invalid value for key "+key+": "+value)
          elif aggregateLevel == "monthly":
            dateTest = aggregate[0]+"-01"
            if not validate(dateTest):
              sys.exit("Key was not a date: "+str(aggregate[0]))
            for key,value in aggregate[1].iteritems():
              keyCounter += 1
              if keyCounter > 1:
                sys.exit("Too many keys: "+aggregate[1])
              if key != "unique_questions":
                sys.exit("Invalid key: "+key)
              if not isinstance(value, int):
                sys.exit("Invalid value for key "+key+": "+value)
          elif aggregateLevel == "daily":
            dateTest = aggregate[0]
            if not validate(dateTest):
              sys.exit("Key was not a date: "+str(aggregate[0]))
            for key,value in aggregate[1].iteritems():
              keyCounter += 1
              if keyCounter > 1:
                sys.exit("Too many keys: "+aggregate[1])
              if key != "unique_questions":
                sys.exit("Invalid key: "+key)
              if not isinstance(value, int):
                sys.exit("Invalid value for key "+key+": "+value)
          elif aggregateLevel == "yearly":
            dateTest = aggregate[0]
            match = re.compile("^\d{4}$")
            if not match.match(dateTest):
              sys.exit("Key was not a year: "+str(aggregate[0]))
            for key,value in aggregate[1].iteritems():
              keyCounter += 1
              if keyCounter > 1:
                sys.exit("Too many keys: "+aggregate[1])
              if key != "unique_questions":
                sys.exit("Invalid key: "+key)
              if not isinstance(value, int):
                sys.exit("Invalid value for key "+key+": "+value)
      else:
        sys.exit("File too large for sanity check, please verify manually.")
      print "Question history passed sanity check"
