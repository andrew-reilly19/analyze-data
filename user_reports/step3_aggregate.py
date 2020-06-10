#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np
import datetime

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

df = pd.read_csv (path+'utterances_annotated.csv')
df['startTime'] =  pd.to_datetime(df['startTime'])
df['endTime'] =  pd.to_datetime(df['endTime'])
meetings = df.meeting.unique()
meetingsdf = pd.DataFrame(meetings)
df = df.sort_values(by=['startTime'])

'''
For aggregate meeting stats, filter overall df by utterances for one specific user
    - Amy D : jMZgnpJrX1QwAN0oUkYNme9kD4b2
    - Beth : GcOHEObyGzTShEOpSzma6VpzT2Q2
    - Mike : V4Kc1uN0pgP7oVhaDjcmp6swV2F3
    - John Doucette : FJwf8UtoqvRJ4jnAaqzV5hcfxAG3
    - Brec Hanson : i6T3a2s5WpPo1dxZaRmIJlkFn4m1
    - Jordan : SDzkCh0CetQsNw2gUZS5HPX2FCe2
'''
#mike is in 4 meetings of the 5 test meetings
select_participant = 'V4Kc1uN0pgP7oVhaDjcmp6swV2F3'
#user_df.meeting.unique()
dftest = df[df['meeting']=='music-2']


meeting_length = []
meeting_date = []
meeting_user_count = []
user_speaking_time = []
user_interruptions = []
user_affirmations = []
user_influenced = []
user_interrupted = []
user_affirmed = []
user_influences = []

all_participants = df.participant.unique()
ap_dict = {key: 0 for key in all_participants}

#Meeting Name, Date, length (mins)), users count, Target user speaking time (sec), count user interruptions, count user affirmations,
#   count user influences, count user interruptees, count user affirmed, count user influenced

for meeting in meetings:
    intermediateDF = df[df['meeting']==meeting]
    #meeting
    m_start = intermediateDF.startTime.min()
    m_end = intermediateDF.endTime.max()
    m_date = m_start.date()
    meeting_date.append(m_date)
    #meeting length
    meeting_length_mins = ((m_end-m_start).total_seconds())/60
    meeting_length.append(meeting_length_mins)
    #number of participants
    users = intermediateDF.participant.unique()
    n_users = len(users)
    meeting_user_count.append(n_users)
    if select_participant in users:
        for u in users:
            ap_dict[u] += 1

    #participant information
    userDF = intermediateDF[intermediateDF['participant']==select_participant]
    #speaking time
    user_total_time = userDF.utterance_length.sum()
    user_speaking_time.append(user_total_time)
    #interruption count
    interruptions = userDF.interruption.sum()
    user_interruptions.append(interruptions)
    #affirmations count
    affirmations = userDF.affirmation.sum()
    user_affirmations.append(affirmations)
    #influenced by other user
    influenced = userDF.influenced.sum()
    user_influenced.append(influenced)

    #interrupted by other user
    interrupted = intermediateDF[intermediateDF['interrupts_user']==select_participant].shape[0]
    user_interrupted.append(interrupted)
    #affirmed by other user
    affirmed = intermediateDF[intermediateDF['affirms_user']==select_participant].shape[0]
    user_affirmed.append(affirmed)
    #influences other user
    influences = intermediateDF[intermediateDF['influenced_by_user']==select_participant].shape[0]
    user_influences.append(influences)


meeting_length = pd.DataFrame(meeting_length)
meeting_date = pd.DataFrame(meeting_date)
meeting_user_count = pd.DataFrame(meeting_user_count)
user_speaking_time = pd.DataFrame(user_speaking_time)
user_interruptions = pd.DataFrame(user_interruptions)
user_affirmations = pd.DataFrame(user_affirmations)
user_influenced = pd.DataFrame(user_influenced)
user_interrupted = pd.DataFrame(user_interrupted)
user_affirmed = pd.DataFrame(user_affirmed)
user_influences = pd.DataFrame(user_influences)

meetingsdf = pd.concat([meetingsdf, meeting_length, meeting_date, meeting_user_count, user_speaking_time, user_interruptions], axis=1)
meetingsdf = pd.concat([meetingsdf, user_affirmations, user_influenced, user_interrupted, user_affirmed, user_influences], axis=1)

meetingsdf.columns = ['meeting_name','meeting_length_mins','meeting_date','total_participants','SU_speaking_time','SU_interruptions','SU_affirmations','SU_influenced_by','SU_interrupted','SU_affirmed','SU_influences']

#writing out basic meetings data
outpath = path + select_participant + '/'
df.to_csv(outpath + 'all_meetings_aggregates.csv', index = None)


common_users = pd.DataFrame(list(ap_dict.items()), columns=['user','shared_meetings'])
common_users = common_users[(common_users['user']!=select_participant) & (common_users['shared_meetings']>1)]
most_common_buddy = common_users[(common_users['shared_meetings']==common_users.shared_meetings.max())].iloc[0]['user']












