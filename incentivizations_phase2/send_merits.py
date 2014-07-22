import csv, requests, time, re, sys, random, smtplib, jinja2, envelopes

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Imports from files that I've defined
import helpers

NOBLE_GASSES = []

def read_winner_data(data_full_path):
  winner_list = []
  with open(data_full_path,'r') as f:
    next(f) #ignore the first header row
    for line in f:
      info = line.split(',')
      user_info = {}
      user_info['user_id'] = int(info[0])
      user_info['date'] = time.strptime(info[1], '%Y-%m-%d')
      user_info['username'] = info[2][1:-1] if info[2][0] == '"' else info[2]
      user_info['number_of_new_merits'] = int(info[3])
      user_info['number_of_total_merits'] = int(info[4])
      user_info['change_in_badge_level'] = int(info[5])
      user_info['new_badge_levels'] = [int(x) for x in info[5:10]]
      user_info['merits_per_new_level'] = [int(x) for x in info[11:16]]
      user_info['more_levels'] = int(info[17])
      user_info['merits_until_next_level'] = int(info[18])
      user_info['next_level'] = int(info[19])
      winner_list.append(user_info)
  return winner_list


if __name__ == "__main__":

  if len(sys.argv) < 2:
      print "Usage: %s api_key" % (sys.argv[0])
      sys.exit(1)

  #grab the api key from command line
  api_key = sys.argv[1]

  #are we in test mode or do we want to send the emails for real?
  test_mode = True #default to testing. No accidents here
  if test_mode: #setup the necessairy test information
    test_send_from_addr = ''
    test_send_to_addrs = [''] #array of email addresses that would get the test email
    test_email_body = ''

  #grab the configuration from the config file
  config = helpers.get_config('config/config')

  #paths to the data
  data_directory = 'winners_thank_you'
  data_filename = 'winners_2014_07_14.csv'
  data_full_path = 'data/' + data_directory + '/' + data_filename
  winner_list = read_winner_data(data_full_path)

  #paths to the templates
  template_path = 'templates/badge_wednesday_friday'

  query_params = {'api_key': api_key, 'format': 'json'}

  #grab the text of the emails
  #template one first
  plain_filename = config['swagplain']
  html_filename = config['swaghtml']
  plain_text_file = open(template_path + '/' + plain_filename, 'r')
  plain_template = plain_text_file.read()
  plain_text_file.close()

  html_file = open(template_path + '/' + html_filename, 'r')
  html_template_text = html_file.read()
  html_file.close()

  plain_template = jinja2.Template(plain_template)
  html_template = jinja2.Template(html_template)

  for winner in winner_list:
    #pick a random template for the thank you
    context = {}
    plain_text_rendered = plain_template.render(winner)
    html_rendered = html_template.render(winner)
    #TODO send the email!

  if test_mode:
    #now we want to send the tested emails through
    for addr in test_send_to:
      envelope = envelopes.Envelope(
                                    from_addr=(test_send_from_addr),
                                    to_addr=(addr),
                                    subject = 'Test of Badge Script',
                                    text_body = test_email_body
                                    )
      #note that this needs to change for the test emails to go through
      gmail = envelopes.GMailSMTP('', '')
      gmail.send(envelope)

    '''
    msgroot = MIMEMultipart('related')
    subject_text = "Thank you from the SciCast team"
    if test_mode:
        subject_text += " TESTING RUN"
    msgroot['Subject'] = subject_text
    msgroot['From'] = "Awards@scicast.org"
    msgroot['Reply-to'] = "Awards@scicast.org"
#            msgroot['To'] = user_email #insert email here
    msgroot['To'] = '' #send to me for now

    #part1 = MIMEText(html_text,'html')
    part2 = MIMEText(plain_text,'plain')

    msgroot.attach(sci_logo)
    msgalternative.attach(part2)
    msgalternative.attach(part1)



    serverport = config["server"]+":" + config["port"]
    server = smtplib.SMTP(serverport)
    server.ehlo()
    server.starttls()
    server.login(emailuserpass[0],emailuserpass[1])
    print str(userid)+" "+code+" "+email
    print msgroot['Subject']
    server.sendmail("Awards@scicast.org",[email],msgroot.as_string())
    #server.sendmail("Awards@scicast.org",["ssmith@c4i.gmu.edu"],msgroot.as_string())
    server.quit()
    time.sleep(1)
    '''

