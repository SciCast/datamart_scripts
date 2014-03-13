
#!/usr/bin/env python
#
#  Copyright (c) 2013 Gold Brand Software, LLC. and (c) 2014 George Mason University
#  This software was developed under U.S. Government contract number D11PC20062.
#  The U.S. Federal Government is granted unlimited rights as defined in FAR 52.227-14.
#  All other rights reserved.
#

'''get_question_choices.py

   Retrieve question_choices and do some stuff with it.  Notably, find
   badly-constructed choices.

   ctwardy, 2014.
   
'''

import sys
import get_questions as getQ

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s api_key" % (sys.argv[0])
        sys.exit(1)

    api_key = sys.argv[1]
    payload = {'api_key': api_key, 'format': 'json'}

    # Get question data and write link files
    questions = getQ.get_questions(payload)
    print '%d Questions Retrieved' % len(questions)
    odd_questions = {}
    for q in questions:
        id = q['question_id']
        try:
            # Before mid-March 2014, we return a string
            choices=q['choices'].split(',')
        except KeyError:
            # After mid-March 2014, we return a list
            choices = q['choices_list']
        if any([(choice.startswith(' ') or
                 choice.startswith(u'\xa0') or
                 choice.endswith('\r') or
                 choice.endswith('\n') or
                 '?' in choice) for choice in choices]):
            odd_questions[id] = choices

    filename = 'bad_choices.csv'
    print '%d Questions had bad choices. See %s' % (len(odd_questions), filename)
    s = '''
# Questions with bad choices
# Bad choices start with spacelike, end with CR/LF, or include '?'.
# ====================================================================
'''
    with open(filename,'w') as f:
        f.write(s)
        for key, val in odd_questions.iteritems():
            f.write('%s, %s\n' % (key, val))
    

