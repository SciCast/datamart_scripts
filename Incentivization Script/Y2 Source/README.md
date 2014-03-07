Y2 Incentivization process
================

1. Run geolocate.jar: on the HTML access logs. This would receive geolocation information from an IP location database, and would also count the number of logins per user
2. Run getWinners.jar: *Most Important Script* this is where the magic happens. This script would read from several flat-file "databases", would track activity based on any tracked variables, accumulate over all previous time periods, select winners, and output emails and usernames to pass to script 3
3. Run payment.jar: Read in email addresses, selected amazon code, and sent e-mail out using rpost.

Geolocate.jar:
Inputs: geolocate.conf, optional, list of configurations; Access logs for login page; user list, which was returned from the admin users page, only used to tie user ID with username
Outputs: georesults.csv, csv document with geolocation results; users.db: database of users, emails, activity (logins), usernames, etc.

getWinners.jar:
Inputs: user db from geolocate; users_prev.csv, a file used to track previous activity levels for accumulation
Outputs: winnerlog.csv, a running total of who won, what their activity level was, and when they won; newwinners.csv, only that month's winners; users_prev.csv, updated with a new column for that month

payment.jar:
Inputs: newwinners.csv, file from above with winners, e-mail addresses, and real names; bodyfile.txt, email template; amazoncodes.csv, list of amazon codes and whether they had been used or not.

Outputs: emaillog.csv, postive confirmation the code executed, as well as tying code to email address/name; amazoncodes.csv, would add ",USED" after each code sent, immediately after code was sent.


