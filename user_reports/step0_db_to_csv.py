#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew

This is the original conversion file I wrote, it could still use some optimization, though. It
is very rough and loops through the entire array of utterances multiple times.

This takes approximately 5 mins to complete with the large database (staging.riff)
This takes approximately 30 sec to complete with a medium database (gt.riff)

This takes approximately 30 sec to complete with a medium database (riffai.riff)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reportsGT/'
df = pd.read_json (path+'utterancesGT.json', lines=True)
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

