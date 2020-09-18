#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import swifter

path = '/Users/Andrew/Desktop/NCF/Riff/user_reports/'

dfinit = pd.read_csv (path+'all_utterances2.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])

dfinit = dfinit.sort_values(by=['startTime'])
all_meetings = dfinit.meeting.unique()

#smaller df for testing
# selected_meetings = all_meetings[:20]
# df = dfinit[(dfinit['meeting'].isin(selected_meetings))]

#larger df for overall
df = dfinit

#adding on a newish index for joins later
dflen = df.shape[0]
df_cols = list(df.columns.values)
myindex = pd.DataFrame(range(dflen))
df = pd.concat([df,myindex], axis=1)
df_cols.append('myindex')
df.columns = df_cols

meetings = df.meeting.unique()

print("loaded data")

def annotate_interruption(target_start, target_end, target_user, target_len, indiv_meetingDF):
    interruptFlag = 0
    interrupted_user = ""
    if target_len >= 5:
        #3 conditions - A speaks while B is speaking, there is at least a second overlap, A speaks for 5 sec, and B stops before A
        interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_start) & (indiv_meetingDF['endTime']-timedelta(seconds=1)>target_start) & (indiv_meetingDF['endTime']<target_end) & (indiv_meetingDF['participant']!= target_user)]
        if interDF.shape[0] > 0:
            interruptFlag = 1
            interrupted_user = interDF.iloc[0]['participant']
    return([interruptFlag, interrupted_user])

def annotate_affirmations(target_start, target_end, target_user, target_len, indiv_meetingDF):
    affirmflag = 0
    affirms_user = ""
    if (target_len <= 2) & (target_len > .25):
        #print('length condition met')
        #3 conditions - A speaks while B is speaking, there is at least a quarter second overlap, and A stops before B
        #interDF = indiv_meetingDF[((indiv_meetingDF['endTime']-target_start).total_seconds()>.25) & (indiv_meetingDF['endTime']>target_end) & (indiv_meetingDF['participant']!= target_user)]
        interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_start) & (indiv_meetingDF['endTime']+timedelta(seconds=1)>target_end) & (indiv_meetingDF['participant']!= target_user)]# & (indiv_meetingDF['Utterance_Length_secs']>2)]
        if interDF.shape[0] > 0:
            affirmflag = 1
            affirms_user = interDF.iloc[0]['participant']
    return([affirmflag, affirms_user])

def annotate_influence(target_start, target_user, target_len, indiv_meetingDF):
    influencedflag = 0
    influenced_by_user = ""
    #simple calculation - can't be an interruption (other users's end time needs to be before the target users's start time) and within 3 sec
    if target_len > 1:
        interDF = indiv_meetingDF[(indiv_meetingDF['endTime']<target_start) & (indiv_meetingDF['endTime']+timedelta(seconds=3)>target_start) & (indiv_meetingDF['participant']!= target_user)]# & (indiv_meetingDF['Utterance_Length_secs']>2)]
        if interDF.shape[0] > 0:
            influencedflag = 1
            influenced_by_user = interDF.iloc[0]['participant']
    return([influencedflag, influenced_by_user])


def overall_annotation_function(row, max_utterance):
    #getting intermediate dataframe - all possible intersecting utterances within max utterance length + 3 sec
    start_bracket = row['startTime']-timedelta(seconds=max_utterance+3.001)
    end_bracket = row['endTime']
    im_df = df[(df['startTime']>start_bracket) & (df['endTime']<end_bracket)]
    row_start = row['startTime']
    row_end = row['endTime']
    row_user = row['participant']
    row_len = row['Utterance_Length_secs']
    my_index = row['myindex']
    #checking for interruptions
    interr_data = annotate_interruption(target_start=row_start, target_end=row_end, target_user=row_user, target_len=row_len, indiv_meetingDF=im_df)
    interruption_flag[my_index] = interr_data[0]
    interrupts_user[my_index] = interr_data[1]
    #checking for affirmations
    affirm_data = annotate_affirmations(target_start=row_start, target_end=row_end, target_user=row_user, target_len = row_len, indiv_meetingDF=im_df)
    affirm_flag[my_index] = affirm_data[0]
    affirms_user[my_index] = affirm_data[1]
    #checking for influenced_by
    influence_data = annotate_influence(target_start=row_start, target_user=row_user, target_len=row_len, indiv_meetingDF=im_df)
    influenced_by_flag[my_index] = influence_data[0]
    influenced_by_user[my_index] = influence_data[1]

#initializing arrays - this should be one large numpy array at some point...
interruption_flag = {}
interrupts_user = {}
affirm_flag = {}
affirms_user = {}
influenced_by_flag = {}
influenced_by_user = {}
#longest_utterance = round(df.Utterance_Length_secs.max(),3)

count = 0
totalcount = len(meetings)
for m in meetings:
    df2 = df[df['meeting']==m]
    longest_utterance = round(df2.Utterance_Length_secs.max(),3)
    df2.swifter.apply(lambda row: overall_annotation_function(row, longest_utterance), axis=1)
    count = count+1
    print(count," / ",totalcount)


I_Flag = pd.DataFrame(list(interruption_flag.items()), columns=['myindex1','interruption'])
I_User = pd.DataFrame(list(interrupts_user.items()), columns=['myindex2','interrupts_user'])
A_Flag = pd.DataFrame(list(affirm_flag.items()), columns=['myindex3','affirmation'])
A_User = pd.DataFrame(list(affirms_user.items()), columns=['myindex4','affirms_user'])
In_Flag = pd.DataFrame(list(influenced_by_flag.items()), columns=['myindex5','influenced'])
In_User = pd.DataFrame(list(influenced_by_user.items()), columns=['myindex6','influenced_by_user'])

df = df.join(I_Flag, lsuffix='myindex', rsuffix='myindex1')
df = df.join(I_User, lsuffix='myindex', rsuffix='myindex2')
df = df.join(A_Flag, lsuffix='myindex', rsuffix='myindex3')
df = df.join(A_User, lsuffix='myindex', rsuffix='myindex4')
df = df.join(In_Flag, lsuffix='myindex', rsuffix='myindex5')
df = df.join(In_User, lsuffix='myindex', rsuffix='myindex6')

df = df.drop(['myindex','myindex1','myindex2','myindex3','myindex4','myindex5','myindex6'], axis=1)
df.columns = ['_id','participant','startTime','endTime','meeting','utterance_length','interruption','interrupts_user','affirmation','affirms_user','influenced','influenced_by_user']
df.to_csv(path + 'utterances_annotated.csv', index = None)
