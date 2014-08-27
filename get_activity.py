#!/usr/bin/env python
#
#  Copyright (c) 2013 Gold Brand Software, LLC. and (c) 2014 George Mason University
#  This software was developed under U.S. Government contract number D11PC20062.
#  The U.S. Federal Government is granted unlimited rights as defined in FAR 52.227-14.
#  All other rights reserved.
#


'''get_activity.py

   Get daily trade activity and plot.

    # Trades per day graph
    cat <- as.POSIXct(th$traded_at)
    start <- as.POSIXct("2013-11-25 01:00:00 EST")
    #days <- seq(1,ceiling(as.double(Sys.time()-60*60*24 - start)),1)
    label <- as.character(c(25:30,"Dec 1",2:31,"Jan 1",2:31,"Feb 1",2:28))
    nt <- numeric()
    for (d in 1:max(days)) {
     nt[d] <- length(cat[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])
    }

    png("TpD.png", width = 7200, height = 3600, pointsize = 18, res = 360)
    par(mar=c(5,4,4,4))
    plot(days,nt,type="l",lwd=3,xaxt="n",ylim=c(0,max(nt)*1.25),ylab="Trades per Day",xlab="Date")
     par(las=2)
     axis(1,at=days,lab=label[1:length(days)])
   
'''

class DatamartRetrievalException(Exception):pass

import requests
import sys
import time
from numpy import zeros
import textwrap

def validate(payload):
    '''Perform some basic checks on the query string, ie 'payload'.
    '''
    try:
        payload['format']
    except KeyError:
        payload['format'] = 'json'
    try:
        payload['api_key']
    except KeyError:
        raise DatamartRetrievalException()

def get_tpd(payload):
    '''Get trades per day according to parameters in 'payload'.

    @param payload -- key/value dict. eg: {'format': 'json', 'api_key': '96ae0f...'}
    
    '''
    validate(payload)
    r = requests.get("http://datamart.scicast.org/question/", params=payload)
    if r.status_code != requests.codes.ok:
        raise DatamartRetrievalException()
    fmt = payload['format']
    r.encoding = 'utf-8'  # Attempted to force UTF8, but not working.
    if fmt == 'json':
        return r.json()
    elif fmt == 'csv':
        return r.text

def get_links(json_Qs, dot=False, labels=False):
    '''Print a parent/child link list using the 'relationships' key.

    @param json_Qs -- JSON returned by get_questions()
    @param dot -- Set True to build a dotfile rather than a csv file.
    @param labels -- For dot, set True to use shortnames rather than ID#s. Ignored for CSV.

    Assumes the json returned from a /questions/ query will include a relationships dict
    with fields 'source_question_id', and 'destination_question_id'.  Ignores 'kind'.

    '''
    if not dot:
        sep = ', '
        s = 'Parent, Child\n'
    else:
        sep = ' -> '
        s = '''# SciCast Link Diagram
# %s
digraph {

graph [label="SciCast Link Structure\n\n", labelloc=top, fontsize=40];
rankdir=LR; 
ranksep=.3;
node [style=filled, fillcolor="cornsilk:purple3", color=transparent];

subgraph LEGEND {
	 label="Legend";
	 labelloc=top;
	 rankdir=LR;
	 style=solid;
	 nodesep=0.02;
	 Live;
	 Resolved [style=dotted, color=gray];
	 Invalid [shape=Mdiamond, style=dashed, color=gray];
	 Live -> Resolved [style=invis];
	 Resolved -> Invalid [style=invis];
	 #    TBD: Resolved Arcs:    [style=dotted, color=gray]
	 #    TBD: Proposed Arcs:  	[style=dashed, color=blue]
	 }

''' % time.asctime()
        
    for q in json_Qs:
        try:
            links = q['relationships']
            for link in links:
                s += '%s%s%s\n' % (link['destination_question_id'],
                                   sep,
                                   link['source_question_id'])
        except KeyError:
            pass 

    if labels and dot:
        s += '\n# Labels\n'
        s += get_shortnames(json_Qs, dot=True, linksonly=True)
        s += '}\n'
    return s

def get_shortnames(json_Qs, dot=False, linksonly=True):
    '''Return a list of IDs and ShortNames and Roles
    
    @param dot -- Set True to use dot notation rather than csv
                  Dot notation: id [label="id: Shortname"]
    @param linksonly -- Omit nodes without links

    '''

    # Determine which questions are linked to others
    if linksonly:
        has_links = zeros(len(json_Qs)+1, 'bool')
        for q in json_Qs:
            links = q['relationships']
            if len(links) > 0:
                has_links[q['question_id']] = True
                for link in links:
                    has_links[link['destination_question_id']] = True

    s = ''
    wrapper = textwrap.TextWrapper()
    wrapper.width = 17
    for q in json_Qs:
        if linksonly and not has_links[q['question_id']]:
            continue
        sname = q['short_name'].encode('ascii','replace').replace('"','')
        try:
            roles = q['groups'].encode('ascii','replace')
        except AttributeError:
            roles = ''
        if dot:
            label = '%s: %s (%s)' % (q['question_id'], sname, roles[:20])
            if len(roles) > 20:
                label += '...'
            s += '%s [ label="%s"' % (q['question_id'], wrapper.fill(label))
            if 'Invalid' in roles:
                s += ', shape=Mdiamond, style=dashed, color=gray '
            elif q['resolution_at'] != None:
                s += ',style=dotted, color=gray '
            s += ']\n'
        else:
            s += "%s,%s,%s\n" % (q['question_id'], sname, roles)
    return s

def get_registrations(payload):
    pass
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s api_key [keywords]" % (sys.argv[0])
        sys.exit(1)

    api_key = sys.argv[1]
    if len(sys.argv) > 2:
        keywords = sys.argv[2]
        print 'Keywords are ignored for now.'
    payload = {'api_key': api_key, 'format': 'json'}

    # Get question data and write link files
    json_data = get_questions(payload)
    settled = [x for x in json_data if x['resolution_index'] != None]
    invalid = [x for x in json_data if 'Invalid' in x['groups']]
    print "# Total Questions   : %4d" % (len(json_data))
    print "# Resolved Questions: %4d" % (len(settled))
    print "# Invalid Questions : %4d" % (len(invalid))
    print 'Keys: ', json_data[0].keys()
    with open('shortnames.csv','w') as f:
        f.write(get_shortnames(json_data))
    with open('links.dot','w') as f:
        f.write(get_links(json_data, dot=True, labels=True))
    with open('links.csv','w') as f:
        f.write(get_links(json_data, dot=False))

