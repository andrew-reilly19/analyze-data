#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri June 19 14:15:34 2020

@author: andrew

This is the participant-events conversion file, which takes the participant events for each meeting and outputs
the meeting, the raw start and end times, the assumed start and end times (based on a half+1 count of max participants present)
and the maximum number of users
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reportsGT/participanteventsGT.json'
outpath = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reportsGT/'

'''
reading data into dataframe
'''

p_events = []
for line in open(path, 'r'):
    p_events.append(json.loads(line))

sep_dict = p_events[3]
sep_dict.get('_id')

def parse_json_line(original_dict):
    temp_dict = {}
    #parsing the _id
    id_dict = original_dict.get('_id')
    act_id = id_dict.get('$oid')
    temp_dict['_id'] = act_id
    #parsing participants
    part_list = original_dict.get('participants')
    temp_dict['participants']=len(part_list)
    #parsing meeting
    temp_dict['meeting']=original_dict.get('meeting')
    #parsing timestamp
    temp_time = original_dict.get('timestamp')
    act_time = temp_time.get('$date')
    temp_dict['timestamp'] = act_time
    return(temp_dict)

new_dict = []

for d in p_events:
    temp = parse_json_line(d)
    new_dict.append(temp)

p_DF = pd.DataFrame(new_dict)
p_DF['timestamp'] =  pd.to_datetime(p_DF['timestamp'])

'''
processing dataframe
'''

all_meetings = p_DF.meeting.unique()

newer_dicts = []
for m in all_meetings:
    temp_dict={}
    intDF = p_DF[p_DF['meeting']==m]
    max_users = intDF.participants.max()
    raw_start = intDF.timestamp.min()
    raw_end = intDF.timestamp.max()
    #start rule is half + 1 (or half round-up) for less than 6 users and half of the users for more than 6
    if max_users >= 6:
        start_threshold = round(max_users/2,0)
    if max_users < 6:
        start_threshold = round((max_users/2+.5),0)
    #start_threshold = round((max_users/2+.5),0)
    #end_threshold = start_threshold-1
    intDF2 = intDF[intDF['participants']>=start_threshold]
    real_start = intDF2.timestamp.min()
    post_RS = intDF2.timestamp.max()
    intDF3 = intDF[(intDF['timestamp']>post_RS)&(intDF['participants']<=start_threshold)]
    real_end = intDF3.timestamp.min()
    temp_dict['meeting']=m
    temp_dict['max_users']=max_users
    temp_dict['raw_start']=raw_start
    temp_dict['real_start']=real_start
    temp_dict['start_gap']=(real_start-raw_start).total_seconds()
    temp_dict['real_end']=real_end
    temp_dict['raw_end']=raw_end
    temp_dict['end_gap']=(raw_end-real_end).total_seconds()
    temp_dict['meeting_length']=(real_end-real_start).total_seconds()/60
    newer_dicts.append(temp_dict)

meeting_DF = pd.DataFrame(newer_dicts)
testDF = meeting_DF[meeting_DF['max_users']>1]

#average start gap (mins)
ASG = testDF.start_gap.mean()/60
print("Average Start Gap: ",ASG)

#average end gap (mins)
AEG = testDF.end_gap.mean()/60
print("Average End Gap: ",AEG)

#average raw meeting time (mins)
ARMT = (testDF['raw_end']-testDF['raw_start']).mean()
print("Average Raw Meeting Time: ",ARMT.total_seconds()/60)

#average true meeting time (mins)
ATMT = (testDF['real_end']-testDF['real_start']).mean()
print("Average True Meeting Time: ",ATMT.total_seconds()/60)

print("(Note: all times in minutes and only meetings with at least 2 users was counted)")


meeting_DF.to_csv(outpath + 'meetings_processed.csv', index = None)


#week_meetingsdf_noUs = week_meetingsdf_noUs.groupby(['meeting_year','meeting_week']).sum()



#df = pd.read_json (path+'participanteventsGT.json', lines=True)
#print(df.dtypes)










