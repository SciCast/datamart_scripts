import csv, requests, time, re, sys, random, smtplib, jinja2, envelopes

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Imports from files that I've defined
import helpers

if __name__ == "__main__":

  #are we in test mode or do we want to send the emails for real?
  test_mode = True#default to testing. No accidents here

  #grab the configuration from the config file
  config = helpers.get_config('config/config')
  userpass = helpers.get_config('config/userpass')

  #options for the smtp server
  smtp_options = {}
  smtp_options['server'] = config['server']
  smtp_options['port'] = config['port']
  smtp_options['username'] = userpass['smtp_username']
  smtp_options['password'] = userpass['smtp_password']
  smtp_options['from_addr'] = config['from']

  #paths to the data
  data_directory = 'winners_codes'
  data_filename = 'Winners_2014-07-15.csv'
  data_full_path = 'data/' + data_directory + '/' + data_filename
  winner_list = helpers.read_code_winner_data(data_full_path)

  #paths to the templates
  template_path = 'templates/gift_cards'
  #grab the text of the emails
  #template one first
  plain_filename = config['codeplain']
  html_filename = config['codehtml']
  #get plain file
  plain_text_file = open(template_path + '/' + plain_filename, 'r')
  plain_template = plain_text_file.read()
  plain_text_file.close()
  #get html file
  html_file = open(template_path + '/' + html_filename, 'r')
  html_template = html_file.read()
  html_file.close()
  #templates for codes emails
  code_plain_template = jinja2.Template(plain_template)
  code_html_template = jinja2.Template(html_template)


  print "Getting All Users..."
  all_users = helpers.get_data("https://scicast.org/users/index?role=None&traded_since=None", userpass['api_username'], userpass['api_password'])

  current_codes = []
  for winner in winner_list:

    #images that we need to send. Restart this ever time since it can change based on type
    images = []
    images.append(['images/scicast_logo.png', '<@sci_logo>'])
    images.append(['images/amazon.gif', '<@amazon_image>'])

    #pick a random template for the thank you
    if winner['number_of_codes'] > 0:
      plain_template = code_plain_template
      html_template = code_html_template
      subject = 'Amazon Gift Code from Scicast.org'
      for code_number in range(1,winner['number_of_codes']+1):
        winner['code_number'] = code_number
        winner['amazon_code'] = helpers.get_and_mark_amazon_code('data/codes/giftcards.csv', current_codes[:])
        current_codes.append(winner['amazon_code'])
        if not winner['amazon_code']:
          print "no code .... continuing"
          continue
        text_rendered = plain_template.render(winner)
        html_rendered = html_template.render(winner)
        to_addr = helpers.get_email_from_username(all_users, winner["username"])
        to_addr_check = helpers.get_email_from_userid(all_users, winner["user_id"])
        if winner['number_of_codes'] > 1:
          subject += " " + str(winner['code_number']) + ' of ' + str(winner['number_of_codes'])

        if to_addr != to_addr_check or test_addr == None:
          print "error with address " + to_addr + ".... continuing"
          continue
        #send the emails
        if test_mode:
          to_addr = 'jackschultz23@gmail.com'
          print "TEST: " + winner["username"] + ', ' + to_addr + ',' + winner['amazon_code']
          subject += ' Test'
          helpers.send_email(to_addr, smtp_options['from_addr'], subject, text_rendered, html_rendered, smtp_options, images)
        elif to_addr != None:
          to_addr += ".rpost.org"
          print winner['date'].strftime("%x") + ', ' + winner["username"] + ', ' + to_addr + ',' + winner['amazon_code']
      #    helpers.send_email(to_addr, smtp_options['from_addr'], subject, text_rendered, html_rendered, smtp_options, images)

