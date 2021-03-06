#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew

This file will run somewhat slowly - using Riff methods it will add labels to the
utterance data exactly the same way that it is currently done.  This can be used for futher
research or analysis.

Runtime: ~ 2.5 mins on GT data
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports_riffai/'
dfinit = pd.read_csv (path+'knit_utterances_S1_complete.csv')

dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])
dfinit['utterance_length'] = dfinit['Utterance_Length_secs']
dfinit = dfinit.drop('Utterance_Length_secs', axis=1)
dfinit = dfinit.sort_values(by=['startTime'])

all_meetings = dfinit.meeting.unique()

df = dfinit

#adding on a newish index for joins later
dflen = df.shape[0]
df_cols = list(df.columns.values)
myindex = pd.DataFrame(range(dflen))
df = pd.concat([df,myindex], axis=1)
df_cols.append('myindex')
df.columns = df_cols

meetings = df.meeting.unique()
#meetings = ['research-2']

print("loaded data")

def getDurationInSeconds(first_time, second_time):
    duration = second_time-first_time
    return (duration.total_seconds())


def interruption_compare(earlier_utt, later_utt):
    first_check = getDurationInSeconds(later_utt['startTime'], earlier_utt['endTime'])
    second_check = getDurationInSeconds(earlier_utt['endTime'], later_utt['endTime'])
    third_check = getDurationInSeconds(earlier_utt['startTime'], later_utt['startTime'])
    if (first_check > 1) and (second_check > 0) and (third_check > 0):
        return True
    else:
        return False

def affirmation_compare(earlier_utt, later_utt):
    first_check = getDurationInSeconds(later_utt['startTime'], earlier_utt['endTime'])
    second_check = getDurationInSeconds(later_utt['endTime'], earlier_utt['endTime'])
    third_check = getDurationInSeconds(earlier_utt['startTime'], later_utt['startTime'])
    if (first_check > .25) and (second_check > 0) and (third_check > 0):
        return True
    else:
        return False

def influenced_compare(earlier_utt, later_utt):
    only_check = getDurationInSeconds(earlier_utt['endTime'],later_utt['startTime'])
    if (only_check > 0) and (only_check < 3):
        return True
    else:
        return False

annotatedata = pd.DataFrame(columns=['myindex2','interruptions','interrupts_users','affirmations','affirms_users','influenced','influenced_by_users'])

m_count = 1
utt_counter = 0
tot_m_count = len(meetings)
for m in meetings:
    df_meet = df[df['meeting']==m]
    max_length = df_meet.utterance_length.max()
    #print(max_length)
    for index, row in df_meet.iterrows():
        row_myindex = row['myindex']
        start_bracket = row['startTime'] - timedelta(seconds=(max_length+3.001))
        end_bracket = row['startTime'] + timedelta(seconds = 3.001)
        row_user = row['participant']
        df_check = df_meet[(df_meet['startTime'] > start_bracket) & (df_meet['startTime'] < end_bracket) & (df_meet['participant']!=row_user)]
        df_check = df_check.sort_values(by=['startTime'])
        interruption_count = 0
        interrupts_users = []
        affirmation_count = 0
        affirms_users = []
        influenced_count = 0
        influenced_by_users = []
        for index_check, row_check in df_check.iterrows():
            #check if this utterance interrupts another
            if (row['utterance_length']>5):
                interruption_check = interruption_compare(earlier_utt = row_check, later_utt = row)
                if interruption_check == True:
                    interruption_count += 1
                    interrupts_users.append(row_check['participant'])
            #check if this utterance affirms another
            if (row['utterance_length']<2):
                affirmation_check = affirmation_compare(earlier_utt = row_check, later_utt = row)
                if affirmation_check == True:
                    affirmation_count += 1
                    affirms_users.append(row_check['participant'])
            #check if this utterance is influenced by another
            influenced_check = influenced_compare(earlier_utt = row_check, later_utt = row)
            if influenced_check == True:
                influenced_count += 1
                influenced_by_users.append(row_check['participant'])

        #add the data to the annotate_data DF
        annotatedata.at[row_myindex, 'myindex2'] = row_myindex
        annotatedata.at[row_myindex, 'interruptions'] = interruption_count
        annotatedata.at[row_myindex, 'interrupts_users'] = interrupts_users
        annotatedata.at[row_myindex, 'affirmations'] = affirmation_count
        annotatedata.at[row_myindex, 'affirms_users'] = affirms_users
        annotatedata.at[row_myindex, 'influenced'] = influenced_count
        annotatedata.at[row_myindex, 'influenced_by_users'] = influenced_by_users

    print(m_count, "/", tot_m_count)
    m_count += 1


df_out = df.join(annotatedata, lsuffix='myindex', rsuffix='myindex2')
df_out.columns = ['_id','participant','startTime','endTime','meeting','utterance_length','myindex','myindex2','interruptions','interrupts_users','affirmations','affirms_users','influenced','influenced_by_users']
df_out = df_out.drop('myindex2', axis=1)
df_out['interruptions'] = pd.to_numeric(df_out['interruptions'])
df_out['affirmations'] = pd.to_numeric(df_out['affirmations'])
df_out['influenced'] = pd.to_numeric(df_out['influenced'])

df_out.to_csv(path + 'utterances_annotated_S2_complete.csv', index = None)

print("done!")


'''
Testing
'''


#checking if there are any self-interactions
dftesty = df_out.drop(['_id','startTime','endTime','interruptions','affirmations','influenced'], axis=1)
#dftesty = df

def selfcheck(row):
    flag = 0
    user = row['participant']
    interrupted_users = row['interrupts_users']
    affirmed_users = row['affirms_users']
    influenced_by_users = row['influenced_by_users']
    if (user in interrupted_users):
        flag = 1
    if (user in affirmed_users):
        flag=1
    if (user in influenced_by_users):
        flag=1
    return flag

dftesty['self_flag'] = dftesty.apply(lambda row: (selfcheck(row)), axis=1)
dftesty = dftesty[dftesty['self_flag']==1]
dftesty = dftesty.sort_values(by=['meeting'])
print(dftesty.shape[0], '  self-interactions found!')

#mt = dftesty.meeting.unique()


'''
#manually checking the interaction counts

#research1 = df_out[df_out['meeting']=='research-2']
#research1 = df_out[df_out['meeting']=='research-5']

research1 = df_out[df_out['meeting']=='research-25']
total_utterances = research1.shape[0]
print('Total Utterances:', total_utterances)

research2 = research1[research1['affirmations']>0]
#research1.dtypes
research2 = research2.drop(['_id','meeting','myindex'], axis=1)
research2 = research2.sort_values(by=['startTime'])

tot_meet_secs = research1['utterance_length'].sum()
research1['speaking_percentage'] = research1.apply(lambda row: (row['utterance_length']/tot_meet_secs)*100, axis=1)
research1 = research1.drop(['_id','startTime','endTime','meeting', 'interrupts_users','affirms_users','influenced_by_users','myindex'], axis=1)
research1 = research1.groupby(['participant']).sum()
research1 = research1.sort_values(by=['utterance_length'])

#research1.to_csv(path+'july_7th_meeting_aggregates.csv')
'''

'''
research-2 meeting met on 4/22/2020 at 14:00 GMT (10 AM EST)
research-5 meeting met on 4/29/2020 at 14:30 GMT (10:30 AM EST)
research-6 meeting met on 5/6/2020 at 14:30 GMT (10:30 AM EST)
research-10 meeting met on 5/18/2020 at 15:00 GMT (11 AM EST)
research-11 meeting met on 5/22/2020 at 19:30 GMT (3 PM EST)
'''

'''
Writing out .csv files for comparison to model:

July 7th meeting:
research-25

July 13th meeting:
research-26
research-27 (not the one I was a part of)

July 27th meeting:
research-35
'''

#save to desktop
new_out_loc = '/Users/andrew/Desktop/'

selected_meeting = df_out[df_out['meeting']=='research-25']
selected_meeting.drop('myindex', axis=1, inplace=True)

known_users = {'q94yeKPfA7Nf6kp8JQ69NFQ0rQw2':'Burcin','mGZGS6HsATg0nwArrRoXF9yYiuF3':'Andrew','G0DAHoX1U8hbz1IefV2Vq3TmOy72':'Beth',
               'JUQuvggv76ctK1nJNOWvkkf3McT2':'Jordan','V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike','6lOVocg0h4gbF7ou2aEed7NR9R13':'Justin',
               'uDpJiXwIRbO4U04F9pMpi8JcgSd2':'Reeha', 'IvNIIdX0DrYUWlGd8CWILNFJNcT2':'Recorder'}

def add_name(row):
    pid = row['participant']
    return (known_users.get(pid))

def replace_names(row, column):
    pid_list = row[column]
    name_list = []
    for pid in pid_list:
        name_list.append(known_users.get(pid))
    return(name_list)

selected_meeting['user_name'] = selected_meeting.apply(lambda row: add_name(row), axis=1)

selected_meeting['interrupts_users'] = selected_meeting.apply(lambda row: replace_names(row, 'interrupts_users'), axis=1)
selected_meeting['affirms_users'] = selected_meeting.apply(lambda row: replace_names(row, 'affirms_users'), axis=1)
selected_meeting['influenced_by_users'] = selected_meeting.apply(lambda row: replace_names(row, 'influenced_by_users'), axis=1)

selected_meeting.to_csv(new_out_loc + 'july7th_labeled.csv', index=None)




