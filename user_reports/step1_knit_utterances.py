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
'''
max_gap_seconds = 1
max_gap = timedelta(seconds=max_gap_seconds)




df = dfinit

df_cols = list(df.columns.values)

new_index = 0
new_id = {}
new_participant = {}
new_startTime = {}
new_endTime = {}
new_meeting = {}
new_UL = {}

def write_out(index_num, row, e_time):
    new_id[index_num] = row['_id']
    new_participant[index_num] = row['participant']
    new_startTime[index_num] = row['startTime']
    new_endTime[index_num] = e_time
    new_meeting[index_num] = row['meeting']
    U_length = e_time-row['startTime']
    new_UL[index_num] = U_length.total_seconds()

print("beginning big loop...")

#iterate over each meeting
tot_meetings = all_meetings.shape[0]
count_meetings = 1
for m in all_meetings:
    df2 = df[df['meeting']==m]
    #iterate over each participant in each meeting
    users = df2.participant.unique()
    for u in users:
        df3 = df2[df2['participant']==u]
        #while the participant utterances df is not 0
        n_rows = df3.shape[0]
        while n_rows > 0:
            reference_row = df3.iloc[0]
            #if there's only one utterance left, it is it's own utterance
            if n_rows == 1:
                write_out(new_index, reference_row, reference_row.endTime)
                new_index += 1
                df3 = df3[df3['startTime']>reference_row.endTime]
                n_rows = df3.shape[0]
            else:
                #iterates through rows until it finds a gap larger than the allowed gap
                #when it does, it writes out the data to the dictionary, filters rows alread scanned, and starts again
                #until there are no utterances left in the dataframe
                compare_time = reference_row['endTime']
                row_check_num = 1
                while row_check_num < n_rows:
                    check_row = df3.iloc[row_check_num]
                    check_row_time = check_row['startTime']
                    #print(check_row_time)
                    #first check - if it is the last utterance left, it must write out
                    if row_check_num == n_rows-1:
                        compare_time = check_row['endTime']
                        write_out(new_index, reference_row, compare_time)
                        df3 = df3[df3['startTime']>compare_time]
                        new_index += 1
                        n_rows = df3.shape[0]
                        break
                    #second check - if the utterances are far enough apart, write out the full utterance and filter
                    if (check_row_time - compare_time) > max_gap:
                        write_out(new_index, reference_row, compare_time)
                        df3 = df3[df3['startTime']>compare_time]
                        new_index += 1
                        n_rows = df3.shape[0]
                        break
                    #third check - if the utterances aren't far enough apart, take new end time and try again
                    if (check_row_time - compare_time) <= max_gap:
                        compare_time = check_row['endTime']
                        row_check_num += 1



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
