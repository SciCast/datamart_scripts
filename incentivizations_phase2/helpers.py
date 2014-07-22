#This file contains a few different helper functions that could be useful across the application

import smtplib, time, requests, json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


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

  server.sendmail(from_addr,[to_addr],msgroot.as_string())

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
