#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np
import datetime
from datetime import date
import os

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

dfinit = pd.read_csv (path+'utterances_annotated_S2_complete.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])
df = dfinit.sort_values(by=['startTime'])

meeting_info = pd.read_csv(path+'meetings_processed.csv')
meeting_info['real_start'] = pd.to_datetime(meeting_info['real_start'])
meeting_info['real_end'] = pd.to_datetime(meeting_info['real_end'] )


print('loaded data')

'''
meeting averages data
'''


#average of averages
avg_meetingsdf = df.drop(["_id", "interrupts_user", "affirms_user", "influenced_by_user", 'startTime','endTime'], axis=1)
avg_meetingsdf = avg_meetingsdf.groupby(['meeting', 'participant']).sum()
avg_meetingsdf.reset_index(drop=False, inplace=True)

meetings_small = dfinit.meeting.unique()
meetingsdf_small = pd.DataFrame(meetings_small)

meeting_length2 = {}
meeting_date2 = {}

counter = 0
total_meet = len(meetings_small)
for meeting in meetings_small:
    intermediateDF = df[df['meeting']==meeting]
    m_info = meeting_info[meeting_info['meeting']==meeting]
    #meeting
    m_start = m_info['real_start'].min()
    m_end = m_info['real_end'].max()
    m_date = m_start.date()
    meeting_date2[meeting]=m_date
    #meeting length
    meeting_length_mins = ((m_end-m_start).total_seconds())/60
    meeting_length2[meeting]=meeting_length_mins
    counter += 1
    print(counter, ' / ', total_meet)



meeting_length2 = pd.DataFrame(list(meeting_length2.items()), columns=['meeting1','meetinglength'])
meeting_date2 = pd.DataFrame(list(meeting_date2.items()), columns=['meeting2','meetingdate'])

avg_meetingsdf2 = avg_meetingsdf.merge(meeting_length2, how='left', left_on='meeting', right_on='meeting1')
avg_meetingsdf2 = avg_meetingsdf2.merge(meeting_date2, how='left', left_on='meeting',right_on='meeting2')
avg_meetingsdf2 = avg_meetingsdf2.drop(['meeting1','meeting2'],axis=1)

avg_meetingsdf2 = avg_meetingsdf2[avg_meetingsdf2['meetinglength']>5]

#add number of max users
def add_nusers(row):
    meet = row['meeting']
    m_info = meeting_info[meeting_info['meeting']==meet]
    nusers = m_info.iloc[0]['max_users']
    if nusers == 2:
        return("2")
    if nusers<=4:
        return("3-4")
    if nusers<=7:
        return("5-7")
    if nusers>7:
        return("8+")

avg_meetingsdf2['users_in_meeting'] =  avg_meetingsdf2.apply(lambda row: add_nusers(row), axis=1)

#user utterances divide by 60 (turn into minutes) and then get average by dividing by meeting mins
avg_meetingsdf2['avg_user_time'] =  avg_meetingsdf2.apply(lambda row: (row['utterance_length']/60)/row['meetinglength'], axis=1)
avg_meetingsdf2['interruption_avg'] =  avg_meetingsdf2.apply(lambda row: (row['interruption']/(row['utterance_length']/60)), axis=1)
avg_meetingsdf2['affirmation_avg'] =  avg_meetingsdf2.apply(lambda row: (row['affirmation']/(row['utterance_length']/60)), axis=1)
avg_meetingsdf2['influence_avg'] =  avg_meetingsdf2.apply(lambda row: (row['influenced']/(row['utterance_length']/60)), axis=1)

#drop unnecessary data and aggregate all, write out
avg_meeting_out1 = avg_meetingsdf2.drop(['meeting','participant','meetingdate','users_in_meeting', 'interruption','affirmation','influenced'], axis=1)
avg_meeting_out1['group_obj'] = 1
avg_meeting_out1 = avg_meeting_out1.groupby(['group_obj']).mean()

avg_meeting_out1.to_csv(path + 'avg_meeting_stats.csv')

#write out .csv file with average share of talking time per user by number of users
avg_meeting_out2 = avg_meetingsdf2.drop(['meeting','participant','meetingdate','interruption','affirmation','influenced'], axis=1)
avg_meeting_out2['group_obj'] = 1
avg_meeting_out2 = avg_meeting_out2.groupby(['group_obj','users_in_meeting']).mean()

avg_meeting_out2.to_csv(path + 'avg_meeting_stats_w_nusers.csv')



'''
need to aggregate the avg_meetingsdf2 data into average times for all users
'''

print('done!')

