import csv, requests, time, re, sys, random, smtplib, jinja2, envelopes


#Imports from files that I've defined
import helpers

if __name__ == "__main__":

  #are we in test mode or do we want to send the emails for real?
  test_mode = True #default to testing. No accidents here
  if test_mode: #setup the necessairy test information
    test_send_to_addrs = [''] #array of email addresses that would get the test email

  #grab the configuration from the config file
  config = helpers.get_config('config/config')
  userpass = helpers.get_config('config/userpass')

  #options for the smtp server
  smtp_options = {}
  smtp_options['server'] = config['server']
  smtp_options['port'] = config['port']
  smtp_options['username'] = userpass['smtp_username']
  smtp_options['password'] = userpass['smtp_password']

  #paths to the data
  date_string = time.strftime("%Y-%m-%d")
  data_directory = 'winners_thank_you'
  #data_filename = 'Winners_2014-07-21.csv' #+ date_string + '.csv' #TODO this needs to change per day. or be dynamic
  data_full_path = 'data/' + data_directory + '/' + data_filename
  winner_list = helpers.read_thank_you_winner_data(data_full_path)

  #paths to the templates
  template_path = 'templates/thank_you_monday'
  plain_filenames = config['thankplain'].split(',')
  html_filenames = config['thankhtml'].split(',')

#  query_params = {'api_key': api_key, 'format': 'json'}

  #plain templates
  plain_mail_templates = []
  for filename in plain_filenames:
    plain_text_file = open(template_path + '/' + filename, 'r')
    template_text = plain_text_file.read()
    plain_text_file.close()
    plain_mail_templates.append(jinja2.Template(template_text))

  html_mail_templates = []
  for filename in html_filenames:
    html_text_file = open(template_path + '/' + filename, 'r')
    template_text = html_text_file.read()
    html_text_file.close()
    html_mail_templates.append(jinja2.Template(template_text))

  #images that we need to send
  images = []
  images.append(['images/scicast_logo.png', '<@sci_logo>'])


  print "Getting All Users..."
  all_users = helpers.get_data("https://scicast.org/users/index?role=None&traded_since=None", userpass['api_username'], userpass['api_password'])
  import pdb;pdb.set_trace()

  for winner in winner_list:
    #pick a random template for the thank you
    template_index = random.randint(0, len(plain_mail_templates)-1)
    plain_template = plain_mail_templates[template_index]
    html_template = html_mail_templates[template_index]
    text_rendered = plain_template.render(username = winner["username"])
    html_rendered = html_template.render(username = winner["username"])
    subject = "Thank you from the SciCast team"
    to_addr = helpers.get_email_from_username(all_users, winner["username"])
    to_addr_check = helpers.get_email_from_userid(all_users, winner["user_id"])
    if to_addr != to_addr_check:
      print "error with address " + to_addr + ".... continuing"
      continue
    from_addr = config["from"]
    if test_mode:
      to_addr = test_send_to_addrs[0] #just grab the first
    print "Sending email for " + winner["username"] + ' at address ' + to_addr + '.'

    if not test_mode and to_addr != None and False:
      helpers.send_email(to_addr, from_addr, subject, text_rendered, html_rendered, smtp_options, images)


  if test_mode and False:
    #now we want to send the tested emails through
    subject = "Test of Thank You Script"

    for addr in test_send_to_addrs:
      helpers.send_email(addr, config["from"], subject, text_rendered, html_rendered, smtp_options, images)

