#This file contains a few different helper functions that could be useful across the application

import smtplib, datetime, requests, json, time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


ANIMAL_CATEGORIES = ['species', 'genus', 'family', 'order', 'class', 'phylum', 'kingdom']


def get_config(filename):
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

def get_userpass(user_password_file_path):
  userpassfile = open(user_password_file_path, 'r')
  emailuserpass = userpassfile.readline().strip('\n').strip().split(':')
  apiuserpass = userpassfile.readline().strip('\n').strip().split(':')
  userpassfile.close()

def send_email(to_addr, from_addr, subject, body_plain, body_html, smtp_options, images=None):
  '''
  This function sends an email through the GMU smtp server. Both html and plain
  '''

  #we want to bcc important people in
  bcc = None #'tlevitt@gmu.edu'#'kolson8@gmu.edu' #['jack@inklingmarkets.com'] #[]

  msgroot = MIMEMultipart('related')

  msgroot['Subject'] = subject
  msgroot['From'] = from_addr
  msgroot['Reply-to'] = from_addr
  msgroot['To'] = to_addr

  msgalternative = MIMEMultipart('alternative')
  msgroot.attach(msgalternative)

  part1 = MIMEText(body_html,'html')
  part2 = MIMEText(body_plain,'plain')

  msgalternative.attach(part2)
  msgalternative.attach(part1)

  for image in images:
    img_file = open(image[0], 'rb')
    mime_image = MIMEImage(img_file.read())
    img_file.close()
    mime_image.add_header('Content-ID', image[1])
    msgroot.attach(mime_image)

  serverport = smtp_options['server']+":"+smtp_options['port']
  server = smtplib.SMTP(serverport)
  server.ehlo()
  server.starttls()
  server.login(smtp_options['username'],smtp_options['password'])

  server.sendmail(from_addr,[to_addr, None, bcc],msgroot.as_string())

  server.quit()
  time.sleep(1)

def get_data(url, username, password):
  """
  Does a call to targetUrl, parses result to json, returns the json

  @type targetUrl: String
  @param targetUrl: URL to pull data from, with options, etc
  @return: JSON object with results of query
  """
  session = requests.session()
  response = session.get("http://scicast.org/session/create?username="+username+"&password="+password)
  o=None
  response = session.get(url)
  text = response.text
  r = session.get("http://scicast.org/session/destroy")
  try:
      o = json.loads(text)
  except ValueError:
      print "Website return did not match expected format: "+t
      sys.exit()
  return o

def get_email_from_userid(allusers, userid):
    for user in allusers:
        if user["id"] == userid:
            email = user["email"]
            if email is None or email == "":
                print "No email found for "+str(userid)
            return email
    return ""

def get_email_from_username(allusers, username):
    for user in allusers:
        if user["username"] == username:
            email = user["email"]
            if email is None or email == "":
                print "No email found for "+str(username)
            return email
    return None

def read_code_winner_data(data_full_path):
  winner_list = []
  with open(data_full_path,'r') as f:
    next(f) #ignore the first header row
    for line in f:
      info = line.split(',')
      user_info = {}
      user_info['user_id'] = int(info[0])
      user_info['date'] = datetime.datetime.strptime(info[1], '%Y-%m-%d')
      user_info['day_of_week'] = user_info['date'].strftime('%A')
      user_info['username'] = info[2][1:-1] if info[2][0] == '"' else info[2]
      user_info['number_of_codes'] = int(info[3])
      user_info['number_of_new_merits'] = int(info[4])
      user_info['number_of_total_merits'] = int(info[5])
      user_info['change_in_badge_level'] = int(info[6])
      user_info['new_badge_levels'] = [int(x) for x in info[7:13]]
      user_info['merits_per_new_level'] = [int(x) for x in info[13:19]]
      user_info['more_levels'] = int(info[19])
      user_info['merits_until_next_level'] = int(info[20])
      user_info['next_level'] = int(info[21])
      user_info['code_number'] = 1
      winner_list.append(user_info)
  return winner_list

def read_thank_you_winner_data(data_full_path):
  winner_list = []
  with open(data_full_path,'r') as f:
    next(f) #ignore the first header row
    for line in f:
      info = line.split(',')
      user_info = {}
      user_info['user_id'] = int(info[0])
      user_info['date'] = datetime.datetime.strptime(info[1], '%Y-%m-%d')
      user_info['day_of_week'] = user_info['date'].strftime('%A')
      user_info['username'] = info[2][1:-1]
      user_info['number_of_thanks'] = int(info[3])
      winner_list.append(user_info)
  return winner_list

def get_and_mark_amazon_code(infilename, used_codes, test=True):
  '''
  This returns the first code that hasn't been used based on the filename
  as well as isn't in the used_codes array and appends them to a seperate file.
  Note: you're probably going to want to move those lines into the gift card
  file after to update for the next run.
  '''
  outfilename = infilename[:-4] + '_out' + infilename[-4:]
  code = None
  with open(infilename, 'r') as f:
    with open(outfilename, 'a') as dest:
      for line in f:
        split = line.split(',')
        code = split[0].strip('\n')
        if len(split) == 1 and code not in used_codes:
          line_to_write = code + ', USED\n'
          dest.write(line_to_write)
          break
  return code

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

if __name__ == "__main__":
  codes = []
  code = get_and_mark_amazon_code('data/codes/giftcards.csv',codes[:])
  codes.append(code)
  code = get_and_mark_amazon_code('data/codes/giftcards.csv',codes[:])
  codes.append(code)
  code = get_and_mark_amazon_code('data/codes/giftcards.csv',codes[:])
  codes.append(code)
  code = get_and_mark_amazon_code('data/codes/giftcards.csv',codes[:])
  codes.append(code)
  get_and_mark_amazon_code('data/codes/giftcards.csv',codes)
