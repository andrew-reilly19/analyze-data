#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports_riffai/'
dfinit = pd.read_csv (path+'knit_utterances_S1_complete.csv')
#dfinit = pd.read_csv (path+'knit_utterances_S1_complete_1sec.csv')

#dfinit = pd.read_csv (path+'all_utterances_S0_complete.csv')

dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])

dfinit = dfinit.sort_values(by=['startTime'])
all_meetings = dfinit.meeting.unique()

# #smaller df for testing
# selected_meetings = all_meetings[:20]
# df = dfinit[(dfinit['meeting'].isin(selected_meetings))]

#larger df for overall
df = dfinit
#df.dtypes

#adding on a newish index for joins later
dflen = df.shape[0]
df_cols = list(df.columns.values)
myindex = pd.DataFrame(range(dflen))
df = pd.concat([df,myindex], axis=1)
df_cols.append('myindex')
df.columns = df_cols

meetings = df.meeting.unique()

print("loaded data")

def annotate_interruption(target_row, check_utts_df):
    interruptFlag = 0
    interrupted_user = ""
    #3 conditions - A speaks while B is speaking, there is at least a second overlap, A speaks for 5 sec, and B stops before A
    # interruption is at least 5 seconds
    if target_row['Utterance_Length_secs'] > 5:
        #print('length condition met',target_row['Utterance_Length_secs'])
        #can't interrupt yourself
        interDF = check_utts_df[(check_utts_df['participant'] != target_row['participant'])]
        if interDF.shape[0] > 0:
            #someone else needs to be talking when you interrupt
            interDF = interDF[(interDF['startTime']<target_row['startTime'])]
            if interDF.shape[0] > 0:
                interDF = interDF[(interDF['endTime']<target_row['endTime'])]
                if interDF.shape[0] > 0:
                    #needs at least a 1 second overlap
                    interDF = interDF[(interDF['endTime']-timedelta(seconds=1)>target_row['startTime'])]
        #interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_start) & (indiv_meetingDF['endTime']-timedelta(seconds=1)>target_start) & (indiv_meetingDF['endTime']<target_end) & ]
                    if interDF.shape[0] > 0:
                        interruptFlag = interDF.shape[0]
                        interrupted_user = interDF.iloc[0]['participant']
    int_output = [interruptFlag, interrupted_user]
    return(int_output)

def annotate_affirmations(target_row, indiv_meetingDF):
    affirmflag = 0
    affirms_user = ""
    if (target_row['Utterance_Length_secs'] < 2) & (target_row['Utterance_Length_secs'] > .25):
        #print('length condition met', target_row['Utterance_Length_secs'])
        #3 conditions - A speaks while B is speaking, there is at least a quarter second overlap, and A stops before B
        interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_row['startTime']) & (indiv_meetingDF['endTime']>target_row['endTime']) & (indiv_meetingDF['participant']!= target_row['participant'])]
        if interDF.shape[0] > 0:
            affirmflag = interDF.shape[0]
            affirms_user = interDF.iloc[0]['participant']
    aff_output=[affirmflag, affirms_user]
    return(aff_output)

def annotate_influence(target_row, indiv_meetingDF):
    influencedflag = 0
    influenced_by_user = ""
    #simple calculation - can't be an interruption (other users's end time needs to be before the target users's start time) and within 3 sec
    interDF = indiv_meetingDF[(indiv_meetingDF['endTime']<target_row['startTime']) & (indiv_meetingDF['endTime']+timedelta(seconds=3)>target_row['startTime']) & (indiv_meetingDF['participant']!= target_row['participant'])]
    if interDF.shape[0] > 0:
        influencedflag = interDF.shape[0]
        influenced_by_user = interDF.iloc[0]['participant']
    inf_output = [influencedflag, influenced_by_user]
    return(inf_output)


def overall_annotation_function(row, max_utterance, oaf_df):
    #getting intermediate dataframe - all possible intersecting utterances within max utterance length + 3 sec (for influences)
    start_bracket = row['startTime']-timedelta(seconds=(max_utterance+3.01))
    end_bracket = row['startTime']+timedelta(seconds=(3.01))
    my_index = row['myindex']
    im_df = oaf_df[(oaf_df['startTime']>start_bracket) & (oaf_df['endTime']>end_bracket) & (oaf_df['participant']!=row['participant'])]
    #checking for interruptions
    #im_df = oaf_df[oaf_df['participant']!=row['participant']]
    interr_data = annotate_interruption(target_row=row, check_utts_df=im_df)
    interruption_flag[my_index] = interr_data[0]
    interrupts_user[my_index] = interr_data[1]
    #checking for affirmations
    affirm_data = annotate_affirmations(target_row=row, indiv_meetingDF=im_df)
    affirm_flag[my_index] = affirm_data[0]
    affirms_user[my_index] = affirm_data[1]
    #checking for influenced_by
    influence_data = annotate_influence(target_row=row, indiv_meetingDF=im_df)
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
    longest_utterance = df2.Utterance_Length_secs.max()
    for i, r in df2.iterrows():
        overall_annotation_function(row=r, max_utterance=longest_utterance, oaf_df=df2)
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
df.to_csv(path + 'utterances_annotated_S2_complete.csv', index = None)

print("done!")


'''
Testing
'''


#checking if there are any self-interactions
dftesty = df.drop(['_id','startTime','endTime','interruption','affirmation','influenced'], axis=1)
#dftesty = df

def selfcheck(row):
    flag = 0
    user = row['participant']
    if row['interrupts_user']==user:
        flag = 1
    if row['affirms_user']==user:
        flag=0
    if row['influenced_by_user']==user:
        flag=0
    return flag

dftesty['self_flag'] = dftesty.apply(lambda row: (selfcheck(row)), axis=1)
dftesty = dftesty[dftesty['self_flag']==1]
dftesty = dftesty.sort_values(by=['meeting'])

#mt = dftesty.meeting.unique()



#checking the interaction counts

#research1 = df[df['meeting']=='research-2']
research1 = df[df['meeting']=='research-5']

research1 = research1.drop(['_id','startTime','endTime','meeting','affirms_user', 'interrupts_user','influenced_by_user'], axis=1)
research1 = research1.groupby(['participant']).sum()
research1 = research1.sort_values(by=['utterance_length'])

'''
research-2 meeting met on 4/22/2020 at 14:00 GMT (10 AM EST)
research-5 meeting met on 4/29/2020 at 14:30 GMT (10:30 AM EST)
research-6 meeting met on 5/6/2020 at 14:30 GMT (10:30 AM EST)
research-10 meeting met on 5/18/2020 at 15:00 GMT (11 AM EST)
research-11 meeting met on 5/22/2020 at 19:30 GMT (3 PM EST)
'''


derp = dfinit[dfinit['meeting']=='blueleaf-4']


