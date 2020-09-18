#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew

This file is meant to take the json output pulled from the Mongo Database and convert it into a csv
format.  It also removes unnecessary data, such as:
    1-user meetings
    0-length utterances

This is the original conversion file I wrote, it could still use some optimization, though. It
is very rough and loops through the entire array of utterances multiple times.

This takes approximately 5 mins to complete with the large database (staging.riff)
This takes approximately 30 sec to complete with a small-medium database (gt.riff)
This takes approximately 1 min to complete with a medium-large database (riffai.riff)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports_riffai/'
df = pd.read_json (path+'utterancesRAI.json', lines=True)
#print(df.dtypes)

def cleanID(row):
    cell = row['_id']
    val = cell.get("$oid")
    return val

def cleanDate(row, toggle):
    if toggle == 0:
        cell = row['startTime']
    else:
        cell = row['endTime']
    val = cell.get("$date")
    return val

print("extracting ID...")
df['_id'] = df.apply(lambda row: cleanID(row), axis=1)
print("extracting Starttime")
df['startTime'] = df.apply(lambda row: cleanDate(row, toggle = 0), axis=1)
print("extracting Endtime")
df['endTime'] = df.apply(lambda row: cleanDate(row, toggle = 1), axis=1)
print("converting to datetime format...")
df['startTime'] =  pd.to_datetime(df['startTime'])
df['endTime'] =  pd.to_datetime(df['endTime'])
df = df.drop(['volumes','__v'], axis=1)

print("initial cleaning done")

'''
print("processing utterance lengths...")

def utterancelength(row):
    start = row['startTime']
    end = row['endTime']
    u_len = end-start
    return(u_len.total_seconds())

df["Utterance_Length_secs"] = df.apply(lambda row: utterancelength(row), axis=1)

print("removing 0 length utterances...")
df = df[df['Utterance_Length_secs']>0]
'''

print("removing 0 length utterances...")
def zero_length(row):
    if row['endTime']-row['startTime']>timedelta(seconds=0):
        return (1)
    else:
        return (0)

df['flag'] = df.apply(lambda row: zero_length(row), axis=1)
df = df[df['flag']>0]
df = df.drop(['flag'], axis=1)
df = df[df.meeting.notnull()]

print("removing 1-user meetings...")
meetings = df.meeting.unique()

def meeting_participants(m):
    meetingdf = df[df.meeting == m]
    users = meetingdf.participant.unique()
    #print(len(users))
    return len(users)

one_user_meetings = []
for m in meetings:
    nusers = meeting_participants(m)
    if nusers <= 1:
        df = df[df.meeting != m]

print(len(df.meeting.unique()))

print("writing out data")

df.to_csv(path + 'all_utterances_S0_complete.csv', index = None)

#df.to_csv(path + 'all_utterances_S0_complete_w_0s.csv', index = None)



'''
#This section is unnecessary in the whole sequence, it outputs raw utterance data for the specified meeting
#witout the 2-second stitch length

selected_meeting2 = df[df['meeting']=='research-25']

known_users = {'q94yeKPfA7Nf6kp8JQ69NFQ0rQw2':'Burcin','mGZGS6HsATg0nwArrRoXF9yYiuF3':'Andrew','G0DAHoX1U8hbz1IefV2Vq3TmOy72':'Beth',
               'JUQuvggv76ctK1nJNOWvkkf3McT2':'Jordan','V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike','6lOVocg0h4gbF7ou2aEed7NR9R13':'Justin',
               'uDpJiXwIRbO4U04F9pMpi8JcgSd2':'Reeha', 'IvNIIdX0DrYUWlGd8CWILNFJNcT2':'Recorder'}

def add_name(row):
    pid = row['participant']
    return (known_users.get(pid))

selected_meeting2['user_name'] = selected_meeting2.apply(lambda row: add_name(row), axis=1)

selected_meeting2.to_csv(path+'july_7th_research_noknit.csv', index=None)

'''


