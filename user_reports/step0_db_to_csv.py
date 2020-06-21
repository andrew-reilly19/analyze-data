#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew

This is the original conversion file I wrote, it could still use some optimization, though. It
is very rough and loops through the entire array of utterances multiple times.
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

df['_id'] = df.apply(lambda row: cleanID(row), axis=1)
df['startTime'] = df.apply(lambda row: cleanDate(row, toggle = 0), axis=1)
df['endTime'] = df.apply(lambda row: cleanDate(row, toggle = 1), axis=1)
df['startTime'] =  pd.to_datetime(df['startTime'])
df['endTime'] =  pd.to_datetime(df['endTime'])
df = df.drop(['volumes','__v'], axis=1)

def utterancelength(row):
    start = row['startTime']
    end = row['endTime']
    u_len = end-start
    return(u_len.total_seconds())

df["Utterance_Length_secs"] = df.apply(lambda row: utterancelength(row), axis=1)
df = df[df['Utterance_Length_secs']>0]
df = df[df.meeting.notnull()]

meetings = df.meeting.unique()

def meeting_participants(m):
    meetingdf = df[df.meeting == m]
    users = meetingdf.participant.unique()
    print(len(users))
    return len(users)

one_user_meetings = []
for m in meetings:
    nusers = meeting_participants(m)
    if nusers == 1:
        df = df[df.meeting != m]

print(len(df.meeting.unique()))

df.to_csv(path + 'all_utterancesGT.csv', index = None)

'''
old method:
'''

# '''
# first step is to write to a numpy array here (this is how I did it at the time, should be
# re-done completely in pandas)
# '''

# df2 = df.to_numpy()
# #print(df2[1:10,])
# #df2 = df2[:,0:5]

# '''
# second step is to read values out of dictionaries and put them back into their cells
# '''
# def cleanID(cell):
#     val = cell.get("$oid")
#     return val

# def cleanDate(cell):
#     val = cell.get("$date")
#     return val

# def cleanDF(df):
#     rows = df.shape[0]
#     cols = df.shape[1]
#     df_out = np.empty(shape=(rows,cols), dtype="object")
#     for i in range(0,rows):
#         df_out[i,0] = cleanID(df[i,0])
#         df_out[i,1] = df[i,1]
#         df_out[i,2] = cleanDate(df[i,2])
#         df_out[i,3] = cleanDate(df[i,3])
#         df_out[i,4] = df[i,4]
#     return df_out

# df3 = cleanDF(df2)


# '''
# third step is to separate/clean the time/date string into something usable
# '''

# def splitTD(cell):
#     vals = cell.split("T")
#     vals[1] = vals[1].replace("Z", "")
#     return vals

# def separate_Time_and_Date(df):
#     rows = df.shape[0]
#     cols = df.shape[1]
#     df_out = np.empty(shape=(rows,cols+2), dtype="object")
#     for i in range(0,rows):
#         startvals = splitTD(df[i,2])
#         endvals = splitTD(df[i,3])
#         df_out[i,:2] = df[i,:2]
#         df_out[i,2] = df[i,4]
#         df_out[i,3] = startvals[0]
#         df_out[i,4] = startvals[1]
#         df_out[i,5] = endvals[0]
#         df_out[i,6] = endvals[1]
#     return df_out

# df4 = separate_Time_and_Date(df3)

# # newdf = pd.DataFrame(df4)
# # newdf.columns = ['Utterance_ID','Participant_ID',"Meeting_Name","Start_Date","Start_Time","End_Date","End_TIme"]
# # newdf.to_csv('/Users/andrew/Desktop/Riff_Analytics_Internship/ml_utterances.csv', index = None)


# '''
# final step before writing out is to add the utterance length into the dataframe
# '''

# def datecheck(df):
#     n = 0
#     midnightarray = []
#     rows = df.shape[0]
#     for i in range(0,rows):
#         if df[i,3] != df[i,5]:
#             midnightarray.append(i)
#             n=n+1
#             print("different date at: ", i)
#     print(n)
#     return(midnightarray)

# midnightutterances = datecheck(df4)

# def Timefix(cell1, cell2):
#     vals1 = cell1.split(":")
#     vals1 = list(map(float, vals1))
#     vals2 = cell2.split(":")
#     vals2 = list(map(float, vals2))
#     hourdiff = (vals2[0]-vals1[0])*3600
#     mindiff = (vals2[1]-vals1[1])*60
#     secdiff = vals2[2]-vals1[2]
#     totaldiff = hourdiff+mindiff+secdiff #Difference in number of seconds
#     return(round(totaldiff,4))

# def TimeFixDF(df):
#     rows = df.shape[0]
#     cols = df.shape[1]
#     df_out = np.empty(shape=(rows,cols), dtype="object")
#     for i in range(0,rows):
#         df_out[i,:5] = df[i,:5]
#         df_out[i,5] = df[i,6]
#         df_out[i,6] = Timefix(df[i,4],df[i,6])
#         if i in midnightutterances:
#             df_out[i,6] = round(df_out[i,6] + 86400,3)
#     return df_out

# df5 = TimeFixDF(df4)

# # print(df5[389083,])
# # print(df5[759447,])
# # print(df5[813074,])


# newdf = pd.DataFrame(df5)
# newdf.columns = ['Utterance_ID','Participant_ID',"Meeting_Name", "Date", "Start_time","End_time","Utterance_Length_secs"]

# #removing 0 sec utterances
# newdf = newdf[newdf['Utterance_Length_secs']>0]

# #removing utterances without a meeting (don't know why there are here, but they do exist in the database - some kind of fluke?)
# newdf = newdf[newdf.Meeting_Name.notnull()]

# #writing out
# newdf.to_csv(path + 'all_utterances.csv', index = None)
