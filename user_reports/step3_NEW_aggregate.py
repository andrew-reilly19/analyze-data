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

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reportsGT/'

dfinit = pd.read_csv (path+'utterances_annotated_S2_complete.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])
df = dfinit.sort_values(by=['startTime'])

dfraw = pd.read_csv (path+'all_utterances_S0_complete_w_0s.csv')
dfraw['startTime'] =  pd.to_datetime(dfraw['startTime'])
dfraw['endTime'] =  pd.to_datetime(dfraw['endTime'])

meeting_info = pd.read_csv(path+'meetings_processed.csv')
meeting_info['real_start'] = pd.to_datetime(meeting_info['real_start'])
meeting_info['real_end'] = pd.to_datetime(meeting_info['real_end'] )

'''
TESTING:

mecheck = df.meeting.unique()
mecheck = np.array(mecheck)
mecheck = np.sort(mecheck)

research1 = dfinit[dfinit['meeting']=='research-2']
#research1 = dfinit[dfinit['meeting']=='research-5']
#research1 = dfinit[dfinit['meeting']=='research-10']
# mindate = research1.startTime.min()
# maxdate = research1.endTime.max()
# meet_length = maxdate-mindate
# meet_length = meet_length.total_seconds()

research1 = research1.drop(['_id','startTime','endTime','meeting','affirms_user', 'interrupts_user','influenced_by_user'], axis=1)
research1 = research1.groupby(['participant']).sum()
research1 = research1.sort_values(by=['utterance_length'])

tot_utts = research1.utterance_length.sum()
research1['utterance_share'] = research1.apply(lambda row: (row['utterance_length']/tot_utts*100), axis=1)


users = research1.participant.unique()
'''

print('loaded data')

'''
STAGING USERS:
For aggregate meeting stats, filter overall df by utterances for one specific user
    - Amy D : jMZgnpJrX1QwAN0oUkYNme9kD4b2
    - Beth : GcOHEObyGzTShEOpSzma6VpzT2Q2
    - Mike : V4Kc1uN0pgP7oVhaDjcmp6swV2F3
    - John Doucette : FJwf8UtoqvRJ4jnAaqzV5hcfxAG3
    - Brec Hanson : i6T3a2s5WpPo1dxZaRmIJlkFn4m1
    - Jordan : SDzkCh0CetQsNw2gUZS5HPX2FCe2
'''


'''
GT USERS: (from meeting FY20cohort2)
    MLRP_207nuzZNLc8YvoV "Alena"
    MLRP_b8eXeA6wOsLaTGZ "Brian"
    MLRP_4Z6SeqiBce2rVZP "Marc"
    MLRP_9QQIU5xv6Vbferb "Jarred"
'''

'''
Riff AI USERS:
    q94yeKPfA7Nf6kp8JQ69NFQ0rQw2 : Burcin
    mGZGS6HsATg0nwArrRoXF9yYiuF3 : Andrew
    G0DAHoX1U8hbz1IefV2Vq3TmOy72 : Beth
    JUQuvggv76ctK1nJNOWvkkf3McT2 : Jordan
    V4Kc1uN0pgP7oVhaDjcmp6swV2F3 : Mike
'''

known_users = {'MLRP_207nuzZNLc8YvoV':'A','MLRP_b8eXeA6wOsLaTGZ':'B','MLRP_4Z6SeqiBce2rVZP':'M','MLRP_9QQIU5xv6Vbferb':'J'}

#known_users = {'q94yeKPfA7Nf6kp8JQ69NFQ0rQw2':'Burcin', 'mGZGS6HsATg0nwArrRoXF9yYiuF3':'Andrew', 'G0DAHoX1U8hbz1IefV2Vq3TmOy72':'Beth', 'JUQuvggv76ctK1nJNOWvkkf3McT2':'Jordan', 'V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike'}

select_participant = 'MLRP_207nuzZNLc8YvoV'

#only looking at meetings this participant was in
meetings = dfinit[dfinit['participant']==select_participant].meeting.unique()
meetingsdf = pd.DataFrame(meetings)


'''
This section figures out the first plots, on user speaking time.  This should be converted from a single-user approach to a
multi-user approach eventually

This attempts to use a dynamic user count to establish an ideal speaking time for each meeting.  This is done by first
finding the percentage of meeting time that the user was 'present' for (judged by the very first and very last utterance they have)
and dividing that by the total meeting time.  Once each user has a percentage present, this is added together for the dynamic
user count.
'''
#first, getting dynamic user count to create the 'ideal' speaking time for each meeting
p_meetings = dfraw[dfraw['participant']==select_participant].meeting.unique()
d_nusers = {}
our_user = {}
for mtg in p_meetings:
    dfraw2 = dfraw[dfraw['meeting']==mtg]
    #here we filter by what we assume to be the 'real start' and 'real end'
    mtg_info = meeting_info[meeting_info['meeting']==mtg]
    dfraw2 = dfraw2[(dfraw2['startTime'] >= mtg_info.iloc[0]['real_start']) & (dfraw2['startTime'] <= mtg_info.iloc[0]['real_end'])]
    #getting full meeting time
    full_meeting_time = mtg_info.iloc[0]['meeting_length']*60
    dynamic_nusers = 0
    users = dfraw2.participant.unique()
    #looping through each user to find their percentage present
    for user in users:
        dfraw3 = dfraw2[dfraw2['participant']==user]
        u_min = dfraw3.startTime.min()
        u_max = dfraw3.endTime.max()
        u_time = (u_max-u_min).total_seconds()
        u_percent = u_time/full_meeting_time
        dynamic_nusers = dynamic_nusers + u_percent
        if user == select_participant:
            our_user[mtg] = u_percent
    #print(dynamic_nusers)
    ideal_time = 100/dynamic_nusers
    d_nusers[mtg] = ideal_time

#creating dataframe of ideal speaking time
meeting_nusers_dynamic = pd.DataFrame(list(d_nusers.items()), columns=['meeting','ideal_speaking_time'])
our_user = pd.DataFrame(list(our_user.items()), columns = ['meeting1','actual_speaking_time'])
meeting_stats = meeting_nusers_dynamic.merge(our_user, left_on='meeting',right_on='meeting1')
meeting_stats = meeting_stats.drop('meeting1', axis=1)

print('done!')


'''
all_participants = df.participant.unique()
ap_dict = {key: 0 for key in all_participants}

#Meeting Name, Date, length (mins)), users count, Target user speaking time (sec), count user interruptions, count user affirmations,
#   count user influences, count user interruptees, count user affirmed, count user influenced


counter = 0
total_meet = len(meetings)
list_of_dicts=[]
for meeting in meetings:
    temp_dict={}
    intermediateDF = df[df['meeting']==meeting]
    m_info = meeting_info[meeting_info['meeting']==meeting]
    #meeting
    m_start = m_info['real_start'].min()
    m_end = m_info['real_end'].max()
    m_date = m_start.date()
    #meeting length
    meeting_length_mins = ((m_end-m_start).total_seconds())/60
    temp_dict['meeting']=meeting
    temp_dict['meeting_length']=round(meeting_length_mins,4)
    temp_dict['meeting_date']=m_date
    #number of participants
    users = intermediateDF.participant.unique()
    n_users = len(users)
    temp_dict['user_count']=n_users
    for u in users:
        ap_dict[u] += 1

    #participant information
    userDF = intermediateDF[intermediateDF['participant']==select_participant]
    #speaking time
    user_total_time = userDF.utterance_length.sum()
    temp_dict['user_speaking_time']=round(user_total_time/60,4)
    #interruption count
    interruptions = userDF.interruption.sum()
    temp_dict['user_interruptions']=interruptions
    #affirmations count
    affirmations = userDF.affirmation.sum()
    temp_dict['user_affirmations']=affirmations
    #influenced by other user
    influenced = userDF.influenced.sum()
    temp_dict['user_influenced']=influenced

    #interrupted by other user
    interrupted = intermediateDF[intermediateDF['interrupts_user']==select_participant].shape[0]
    temp_dict['user_interrupted']=interrupted
    #affirmed by other user
    affirmed = intermediateDF[intermediateDF['affirms_user']==select_participant].shape[0]
    temp_dict['user_affirmed']=affirmed
    #influences other user
    influences = intermediateDF[intermediateDF['influenced_by_user']==select_participant].shape[0]
    temp_dict['user_influences']=influences

    list_of_dicts.append(temp_dict)
    counter += 1
    print(counter, ' / ', total_meet)

print('finalizing new dataframe...')


'''
