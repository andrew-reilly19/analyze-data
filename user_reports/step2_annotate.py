#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

dfinit = pd.read_csv (path+'all_utterances2.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])

#smaller df for testing
df = dfinit[(dfinit['meeting']=='checkin-1') | (dfinit['meeting']=='beta-2') | (dfinit['meeting']=='music-2')| (dfinit['meeting']=='latenite-1')| (dfinit['meeting']=='beta-5')]

#larger df for overall
#df = dfinit

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
    #checking for interruptions
    interr_data = annotate_interruption(target_start=row_start, target_end=row_end, target_user=row_user, target_len=row_len, indiv_meetingDF=im_df)
    interruption_flag.append(interr_data[0])
    interrupts_user.append(interr_data[1])
    #checking for affirmations
    affirm_data = annotate_affirmations(target_start=row_start, target_end=row_end, target_user=row_user, target_len = row_len, indiv_meetingDF=im_df)
    affirm_flag.append(affirm_data[0])
    affirms_user.append(affirm_data[1])
    #checking for influenced_by
    influence_data = annotate_influence(target_start=row_start, target_user=row_user, target_len=row_len, indiv_meetingDF=im_df)
    influenced_by_flag.append(influence_data[0])
    influenced_by_user.append(influence_data[1])

#initializing arrays - this should be one large numpy array at some point...
interruption_flag = []
interrupts_user = []
affirm_flag = []
affirms_user = []
influenced_by_flag = []
influenced_by_user = []
#longest_utterance = round(df.Utterance_Length_secs.max(),3)

count = 0
totalcount = len(meetings)
for m in meetings:
    df2 = df[df['meeting']==m]
    longest_utterance = round(df2.Utterance_Length_secs.max(),3)
    df2.apply(lambda row: overall_annotation_function(row, longest_utterance), axis=1)
    count = count+1
    print(count," / ",totalcount)


I_Flag = pd.DataFrame(interruption_flag)
I_User = pd.DataFrame(interrupts_user)
A_Flag = pd.DataFrame(affirm_flag)
A_User = pd.DataFrame(affirms_user)
In_Flag = pd.DataFrame(influenced_by_flag)
In_User = pd.DataFrame(influenced_by_user)


df = pd.concat([df, I_Flag], axis=1)
df = pd.concat([df, I_User], axis=1)
df = pd.concat([df, A_Flag], axis=1)
df = pd.concat([df, A_User], axis=1)
df = pd.concat([df, In_Flag], axis=1)
df = pd.concat([df, In_User], axis=1)

df.columns = ['_id','participant','startTime','endTime','meeting','utterance_length','interruption','interrupts_user','affirmation','affirms_user','influenced','influenced_by_user']

df.to_csv(path + 'utterances_annotated.csv', index = None)


#### Testing

# test = {'col_1': [0, 1, 2, 3], 'col_2': [4, 5, 6, 7]}
# dftest = pd.DataFrame(test)

# dflen = dftest.shape[0]
# new1df = []
# new2df = []
# new3df = []

# #pd.DataFrame(range(dflen))
# #dftest['indx'] = range(dflen)

# def test_df(row):
#     one = row['col_1']
#     two = row['col_2']
#     new1 = one * two
#     new1df.append(new1)
#     new2 = one + two
#     new2df.append(new2)
#     new3 = str(one)+str(two)
#     new3df.append(new3)


# dftest.apply(lambda row: test_df(row), axis=1)
# new1df_2 = pd.DataFrame(new1df)
# new2df_2 = pd.DataFrame(new2df)
# new3df_2 = pd.DataFrame(new3df)
# dftest['new1'] = new1df_2
# dftest['new2'] = new2df_2
# dftest['new3'] = new3df_2
