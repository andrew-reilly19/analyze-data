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
import matplotlib.pyplot as plt

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reportsGT/'

dfinit = pd.read_csv (path+'utterances_annotated_S2_complete.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])
df = dfinit.sort_values(by=['startTime'])

# dftesty = dfinit.drop(['_id','startTime','endTime','meeting','utterance_length','interruption','affirmation','influenced'], axis=1)

# def selfcheck(row):
#     flag = 0
#     user = row['participant']
#     if row['interrupts_user']==user:
#         flag = 1
#     if row['affirms_user']==user:
#         flag=1
#     if row['influenced_by_user']==user:
#         flag=1
#     return flag

# dftesty['self_flag'] = dftesty.apply(lambda row: (selfcheck(row)), axis=1)
# dftesty = dftesty[dftesty['self_flag']==1]

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
GT USERS: (from meetings FY20cohort2)
    MLRP_207nuzZNLc8YvoV "Alena"
    MLRP_b8eXeA6wOsLaTGZ "Brian"
    MLRP_4Z6SeqiBce2rVZP "Marc"
    MLRP_9QQIU5xv6Vbferb "Jarred"
    MLRP_2lb2J9sL14bWiLr "Tamara"
    MLRP_2tOntZytvl6j4a1 "Gina"
    MLRP_8kT5pkyD7bYIkm1 "Andrew"

'''

'''
Riff AI USERS:
    q94yeKPfA7Nf6kp8JQ69NFQ0rQw2 : Burcin
    mGZGS6HsATg0nwArrRoXF9yYiuF3 : Andrew
    G0DAHoX1U8hbz1IefV2Vq3TmOy72 : Beth
    JUQuvggv76ctK1nJNOWvkkf3McT2 : Jordan
    V4Kc1uN0pgP7oVhaDjcmp6swV2F3 : Mike
'''

known_users = {'MLRP_207nuzZNLc8YvoV':'Alena','MLRP_b8eXeA6wOsLaTGZ':'Brian','MLRP_4Z6SeqiBce2rVZP':'Marc','MLRP_9QQIU5xv6Vbferb':'Jarred','MLRP_2lb2J9sL14bWiLr':'Tamara', 'MLRP_2tOntZytvl6j4a1':'Gina', 'MLRP_8kT5pkyD7bYIkm1':'Andrew'}

#known_users = {'q94yeKPfA7Nf6kp8JQ69NFQ0rQw2':'Burcin', 'mGZGS6HsATg0nwArrRoXF9yYiuF3':'Andrew', 'G0DAHoX1U8hbz1IefV2Vq3TmOy72':'Beth', 'JUQuvggv76ctK1nJNOWvkkf3McT2':'Jordan', 'V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike'}

select_participant = 'MLRP_207nuzZNLc8YvoV'


'''
This section figures out the first plots, on user speaking time.  This should be converted from a single-user approach to a
multi-user approach eventually

This attempts to use a dynamic user count to establish an ideal speaking time for each meeting.  This is done by first
finding the percentage of meeting time that the user was 'present' for (judged by the very first and very last utterance they have)
and dividing that by the total meeting time.  Once each user has a percentage present, this is added together for the dynamic
user count.
'''
#first, getting dynamic user count to create the 'ideal' speaking time for each meeting
p_meet = dfraw[dfraw['participant']==select_participant].meeting.unique()
p_meetings = []
#dropping meetings with only 1 user and less than 5 mins (likely not the main meeting)
for m in p_meet:
    meettest = meeting_info[meeting_info['meeting']==m]
    if (meettest.iloc[0]['max_users'] > 1) & (meettest.iloc[0]['meeting_length']>5):
        p_meetings.append(m)


#loop to find the ideal speaking time per meeting
d_nusers = {}
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
    #print(dynamic_nusers)
    ideal_time = 100/dynamic_nusers
    d_nusers[mtg] = ideal_time

#creating dataframe of ideal speaking time
meeting_ideal = pd.DataFrame(list(d_nusers.items()), columns=['meeting1','ideal_speaking_time'])

print("Ideal speaking times found")

#trimming the meeting utterancews for later
total_meeting_data = df[df.meeting.isin(p_meetings)]

def trim_utterance_prep(row):
    flag = 0
    mtg_info = meeting_info[meeting_info['meeting']==row['meeting']]
    if (row['startTime'] >= mtg_info.iloc[0]['real_start']) & (row['startTime'] <= mtg_info.iloc[0]['real_end']):
        flag = 1
    return flag

total_meeting_data['trimflag'] = total_meeting_data.apply(lambda row: trim_utterance_prep(row), axis=1)
trimmed_meeting_data = total_meeting_data[total_meeting_data['trimflag']==1]
trimmed_meeting_data = trimmed_meeting_data.drop(['_id','trimflag','interrupts_user','affirms_user','influenced_by_user', 'startTime','endTime'], axis=1)

print("Utterances Trimmed")
#Trimmed and aggregate meeting data here will be used for the rest of the plotting

agg_meeting_data = trimmed_meeting_data.groupby(['participant','meeting']).sum().reset_index()

def get_speaking_percentage(row, thisdf):
    thisdf2 = thisdf[thisdf['meeting']==row['meeting']]
    tot_utt_length = thisdf2.utterance_length.sum()
    user_SP = row['utterance_length']
    return (user_SP/tot_utt_length*100)

agg_meeting_data['speaking_percentage'] = agg_meeting_data.apply(lambda row: (get_speaking_percentage(row, agg_meeting_data)), axis=1)

print("Finalizing dataframe")

all_meeting_data = agg_meeting_data.merge(meeting_ideal, left_on='meeting',right_on='meeting1')

def add_date(row):
    rowmeet = row['meeting']
    rowdate = meeting_info[meeting_info['meeting']==rowmeet].iloc[0]['real_start'].strftime("%B %-d")
    return(rowdate)

all_meeting_data['date'] = all_meeting_data.apply(lambda row: add_date(row), axis=1)
all_meeting_data = all_meeting_data.drop('meeting1', axis=1)


print("Producing plots")

our_user = all_meeting_data[all_meeting_data['participant']==select_participant]
our_user.set_index('date', inplace=True)
#our_user = our_user.sort_values(by=['date'])

outpath = path+select_participant+'/'

our_user.to_csv(outpath +select_participant+'_data.csv')

if not os.path.exists(outpath):
    os.mkdir(outpath)

#TODO: need to make these lines curvy instead of jagged

img_size = (7,4)

fig1 = plt.figure(figsize=img_size)
our_user['speaking_percentage'].plot(color = 'dodgerblue', linewidth=2.0, use_index=True, label='You')
our_user['ideal_speaking_time'].plot(kind='bar', color = 'chocolate', use_index=True, label='Ideal')
plt.xlabel('Date')
plt.ylabel('% Speaking Time')
plt.legend(loc="best")
fig1.savefig(outpath+'img1.png',bbox_inches='tight')
plt.close(fig1)


fig2 = plt.figure(figsize=img_size)
our_user['interruption'].plot(color='firebrick',linewidth=2.0, use_index=True)
plt.xlabel('Date')
plt.ylabel('Interruptions')
plt.xticks(rotation='vertical')
fig2.savefig(outpath+'img2.png',bbox_inches='tight')
plt.close(fig2)


fig3 = plt.figure(figsize=img_size)
our_user['affirmation'].plot(color='forestgreen',linewidth=2.0, use_index=True)
plt.xlabel('Date')
plt.ylabel('Affirmations')
plt.xticks(rotation='vertical')
fig3.savefig(outpath+'img3.png',bbox_inches='tight')
plt.close(fig3)


#TODO: currently this shows the number of times they were influenced, not the other way around - needs to be fixed
fig4 = plt.figure(figsize=img_size)
our_user['influenced'].plot(color='gold',linewidth=2.0, use_index=True)
plt.xlabel('Date')
plt.ylabel('Influences')
plt.xticks(rotation='vertical')
fig4.savefig(outpath+'img4.png',bbox_inches='tight')
plt.close(fig4)

print('first 4 plots complete')

#Now onto the boxplots
a_users = all_meeting_data.participant.unique()
imp_users = [select_participant]
for user in a_users:
    if user != select_participant:
        udf = all_meeting_data[all_meeting_data['participant']==user]
        if udf.shape[0]>1:
            imp_users.append(user)


speaking_time = []
interruptions = []
affirmations = []
influences = []
user_name = ['You!']

for user in imp_users:
    udf = all_meeting_data[all_meeting_data['participant']==user]
    sp_list = udf['speaking_percentage'].to_list()
    int_list = udf['interruption'].to_list()
    aff_list = udf['affirmation'].to_list()
    inf_list = udf['influenced'].to_list()
    speaking_time.append(sp_list)
    interruptions.append(int_list)
    affirmations.append(aff_list)
    influences.append(inf_list)
    if user != select_participant:
        user_name.append(known_users.get(user))



fig5 = plt.figure(1, figsize=img_size)
ax5 = fig5.add_subplot(111)
bp5 = ax5.boxplot(speaking_time,patch_artist=True, meanline=True)
ax5.set_xticklabels(user_name, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Speaking Time %')
for box in bp5['boxes']:
    # change fill color
    box.set( facecolor = 'royalblue' )
## change color and linewidth of the medians
for mean in bp5['means']:
    mean.set(color='black', linewidth=2)
fig5.savefig(outpath+'img5.png',bbox_inches='tight')
plt.close(fig5)


fig6 = plt.figure(1, figsize=img_size)
ax6 = fig6.add_subplot(111)
bp6 = ax6.boxplot(interruptions,patch_artist=True, meanline=True)
ax6.set_xticklabels(user_name, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Interruptions')
for box in bp6['boxes']:
    # change fill color
    box.set( facecolor = 'firebrick' )
## change color and linewidth of the medians
for mean in bp6['means']:
    mean.set(color='black', linewidth=2)
fig6.savefig(outpath+'img6.png',bbox_inches='tight')
plt.close(fig6)

fig7 = plt.figure(1, figsize=img_size)
ax7 = fig7.add_subplot(111)
bp7 = ax7.boxplot(affirmations,patch_artist=True, meanline=True)
ax7.set_xticklabels(user_name, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Affirmations')
for box in bp7['boxes']:
    # change fill color
    box.set( facecolor = 'forestgreen' )
## change color and linewidth of the medians
for mean in bp7['means']:
    mean.set(color='black', linewidth=2)
fig7.savefig(outpath+'img7.png',bbox_inches='tight')
plt.close(fig7)

fig8 = plt.figure(1, figsize=img_size)
ax8 = fig8.add_subplot(111)
bp8 = ax8.boxplot(influences,patch_artist=True, meanline=True)
ax8.set_xticklabels(user_name, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Influences')
for box in bp8['boxes']:
    # change fill color
    box.set( facecolor = 'gold' )
## change color and linewidth of the medians
for mean in bp8['means']:
    mean.set(color='black', linewidth=2)
fig8.savefig(outpath+'img8.png',bbox_inches='tight')
plt.close(fig8)

print('complete!')




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
