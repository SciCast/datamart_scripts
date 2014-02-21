#!/usr/bin/env python
#
#  Copyright (c) 2013 Gold Brand Software, LLC.
#  This software was developed under U.S. Government contract number D11PC20062.
#  The U.S. Federal Government is granted unlimited rights as defined in FAR 52.227-14.  All other rights reserved.
#
#
#

class DatamartRetrievalException(Exception):pass

import requests
import sys

def get_question_as_json(api_key):
    location = "http://datamart.scicast.org/question/?format=json&api_key=%s"%(api_key)
    r = requests.get(location)
    if r.status_code != 200:
        raise DatamartRetrievalException()
    return r.json()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        json_data = get_question_as_json(api_key = api_key)
        print "Total Questions: %s"%(len(json_data))
        for q in json_data:
            print "%s,%s\n"%(q['id'],q['name'])

    else:
        print "Usage: %s api_key"%(sys.argv[0])
