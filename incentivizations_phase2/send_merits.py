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
  data_directory = 'winners_badges'
  data_filename = 'Winners_2014-07-15.csv'
  data_full_path = 'data/' + data_directory + '/' + data_filename
  winner_list = helpers.read_code_winner_data(data_full_path)

  #paths to the templates
  template_path = 'templates/badges'
  #now get just the badge templates....
  #template one first
  plain_filename = config['swagplain']
  html_filename = config['swaghtml']
  #get plain file
  plain_text_file = open(template_path + '/' + plain_filename, 'r')
  plain_template = plain_text_file.read()
  plain_text_file.close()
  #get html file
  html_file = open(template_path + '/' + html_filename, 'r')
  html_template = html_file.read()
  html_file.close()
  #templates for codes emails
  swag_plain_template = jinja2.Template(plain_template)
  swag_html_template = jinja2.Template(html_template)

  print "Getting All Users..."
  all_users = helpers.get_data("https://scicast.org/users/index?role=None&traded_since=None", userpass['api_username'], userpass['api_password'])

  current_codes = []
  for winner in winner_list:

    #images that we need to send. Restart this ever time since it can change based on type
    images = []
    images.append(['images/scicast_logo.png', '<@sci_logo>'])

    if winner['number_of_new_merits'] > 0: #just a sanity check
      #we need to figure out which images to put in there. badgewise
      subject = "You've won merits on SciCast.org!"
      plain_template = swag_plain_template
      html_template = swag_html_template
      #we need to figure out which images to attach
      if winner['new_badge_levels'][0]:
        images.append(['images/swag_1_species.png', '<@swag_1_species>'])
      if winner['new_badge_levels'][1]:
        images.append(['images/swag_2_genus.png', '<@swag_2_genus>'])
      if winner['new_badge_levels'][2]:
        images.append(['images/swag_3_family.png', '<@swag_3_family>'])
      if winner['new_badge_levels'][3]:
        images.append(['images/swag_4_order.png', '<@swag_4_order>'])
      if winner['new_badge_levels'][4]:
        images.append(['images/swag_5_class.png', '<@swag_5_class>'])
      if winner['new_badge_levels'][5]:
        images.append(['images/swag_6_phylum.png', '<@swag_6_phylum>'])
  #    if winner['new_badge_levels'][6]:
  #      images.append(['images/swag_7_kingdom.png', '<@swag_7_kingdom>'])

      text_rendered = plain_template.render(winner)
      html_rendered = html_template.render(winner)
      to_addr = helpers.get_email_from_username(all_users, winner["username"])
      to_addr_check = helpers.get_email_from_userid(all_users, winner["user_id"])
      if to_addr != to_addr_check or to_addr == None:
        print "error with address " + to_addr + ".... continuing"
        continue
      #send the emails
      if test_mode:
        to_addr = 'jackschultz23@gmail.com'
        subject += ' Test'
        for index in range(0,len(winner['new_badge_levels'])):
          if winner['new_badge_levels'][index] != 0:
            print winner['date'].strftime("%x") + ', ' + winner["username"] + ', ' + to_addr + ',' + helpers.ANIMAL_CATEGORIES[index]
        helpers.send_email(to_addr, smtp_options['from_addr'], subject, text_rendered, html_rendered, smtp_options, images)
      elif to_addr != None:
        print "AsdFASDFASFASFSD"
        import pdb;pdb.set_trace()
        to_addr += ".rpost.org"
        for index in range(0,len(winner['new_badge_levels'])):
          if winner['new_badge_levels'][index] != 0:
            print winner['date'].strftime("%x") + ', ' + winner["username"] + ', ' + to_addr + ',' + helpers.ANIMAL_CATEGORIES[index]
     #   helpers.send_email(to_addr, smtp_options['from_addr'], subject, text_rendered, html_rendered, smtp_options, images)

