#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew

This is meant to knit the utterances together to get better metrics down the line

Runtime: ~3 mins on GT dataset

"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports_riffai/'
dfinit = pd.read_csv (path+'all_utterances_S0_complete.csv')


dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])

dfinit = dfinit.sort_values(by=['startTime'])
all_meetings = dfinit.meeting.unique()


'''
number of seconds between utterances allowed:
    2 is what Riff currently uses
'''
min_gap_seconds = 2
min_gap = timedelta(seconds=min_gap_seconds)

df = dfinit

df_cols = list(df.columns.values)

new_index = 0
new_id = {}
new_participant = {}
new_startTime = {}
new_endTime = {}
new_meeting = {}
new_UL = {}

def write_out(index_num, row):
    new_id[index_num] = row['_id']
    new_participant[index_num] = row['participant']
    new_startTime[index_num] = row['startTime']
    new_endTime[index_num] = row['endTime']
    new_meeting[index_num] = row['meeting']
    U_length = row['endTime']-row['startTime']
    new_UL[index_num] = U_length.total_seconds()

print("processing utterances...")

#iterate over each meeting
tot_meetings = all_meetings.shape[0]
count_meetings = 1
for m in all_meetings:
    df2 = df[df['meeting']==m]
    #iterate over each participant in each meeting
    users = df2.participant.unique()
    for u in users:
        df3 = df2[df2['participant']==u]
        df3 = df3.sort_values(by=['startTime'])
        cur_utt = df3.iloc[0]
        for index, row in df3.iterrows():
            if row['startTime'] - cur_utt['endTime'] < min_gap:
                cur_utt['endTime']=row['endTime']
            else:
                write_out(new_index,cur_utt)
                new_index += 1
                cur_utt = row
        write_out(new_index,cur_utt)
        new_index += 1

    print(count_meetings," / ",tot_meetings)
    count_meetings += 1


print("Total Utterances: ", new_index)
print("Writing out final data...")

new_id = pd.DataFrame(list(new_id.items()), columns=['myindex1','_id'])
new_participant = pd.DataFrame(list(new_participant.items()), columns=['myindex2','participant'])
new_startTime = pd.DataFrame(list(new_startTime.items()), columns=['myindex3','startTime'])
new_endTime = pd.DataFrame(list(new_endTime.items()), columns=['myindex4','endTime'])
new_meeting = pd.DataFrame(list(new_meeting.items()), columns=['myindex5','meeting'])
new_UL = pd.DataFrame(list(new_UL.items()), columns=['myindex6','Utterance_Length_secs'])

df_out = new_id.join(new_participant, lsuffix='myindex1', rsuffix='myindex2')
df_out = df_out.join(new_startTime, lsuffix='myindex1', rsuffix='myindex3')
df_out = df_out.join(new_endTime, lsuffix='myindex1', rsuffix='myindex4')
df_out = df_out.join(new_meeting, lsuffix='myindex1', rsuffix='myindex5')
df_out = df_out.join(new_UL, lsuffix='myindex1', rsuffix='myindex6')

df_out = df_out.drop(['myindex1','myindex2','myindex3','myindex4','myindex5','myindex6'], axis=1)
df_out = df_out.sort_values(by=['startTime'])


df_out.to_csv(path + 'knit_utterances_S1_complete.csv', index = None)


print("Done!")



'''
for verification


dftest = df_out
# dftest = dftest.sort_values(by=['meeting','startTime'])
# dftest2 = dftest.drop(['_id','participant','endTime','Utterance_Length_secs'], axis=1)
# dftest2 = dftest2.groupby('meeting').first()

#research-2 meeting met on 4/22/2020 at 14:00 GMT (10 AM EST)
#should be 450 utterances
research1 = dftest[dftest['meeting']=='research-2']
print('4/22/2020 Utterance count = ', research1.shape[0])

#research-5 meeting met on 4/29/2020 at 14:30 GMT (10:30 AM EST)
#should be 303 utterances
research1 = dftest[dftest['meeting']=='research-5']
print('4/29/2020 Utterance count = ', research1.shape[0])

#research-6 meeting met on 5/6/2020 at 14:30 GMT (10:30 AM EST)
#should be 518 utterances
research1 = dftest[dftest['meeting']=='research-6']
print('5/6/2020 Utterance count = ', research1.shape[0])

#research-10 meeting met on 5/18/2020 at 15:00 GMT (11 AM EST)
#should be 290 utterances
research1 = dftest[dftest['meeting']=='research-10']
print('5/18/2020 Utterance count = ', research1.shape[0])

#research-11 meeting met on 5/22/2020 at 19:30 GMT (3 PM EST)
#should be 401 utterances
research1 = dftest[dftest['meeting']=='research-11']
print('5/22/2020 Utterance count = ', research1.shape[0])

'''
