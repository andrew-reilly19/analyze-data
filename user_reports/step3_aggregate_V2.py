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
import statistics

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

#known_users = {'MLRP_207nuzZNLc8YvoV':'Alena','MLRP_b8eXeA6wOsLaTGZ':'Brian','MLRP_4Z6SeqiBce2rVZP':'Marc','MLRP_9QQIU5xv6Vbferb':'Jarred','MLRP_2lb2J9sL14bWiLr':'Tamara', 'MLRP_2tOntZytvl6j4a1':'Gina', 'MLRP_8kT5pkyD7bYIkm1':'Andrew'}

known_users = {'MLRP_207nuzZNLc8YvoV':'One','MLRP_b8eXeA6wOsLaTGZ':'Two','MLRP_4Z6SeqiBce2rVZP':'Three','MLRP_9QQIU5xv6Vbferb':'Four','MLRP_2lb2J9sL14bWiLr':'Five', 'MLRP_2tOntZytvl6j4a1':'Six', 'MLRP_8kT5pkyD7bYIkm1':'Seven'}


#known_users = {'q94yeKPfA7Nf6kp8JQ69NFQ0rQw2':'Burcin', 'mGZGS6HsATg0nwArrRoXF9yYiuF3':'Andrew', 'G0DAHoX1U8hbz1IefV2Vq3TmOy72':'Beth', 'JUQuvggv76ctK1nJNOWvkkf3McT2':'Jordan', 'V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike'}

select_participant = 'MLRP_9QQIU5xv6Vbferb'


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
trimmed_meeting_data = trimmed_meeting_data.drop(['_id','trimflag','interrupts_users','affirms_users','influenced_by_users', 'startTime','endTime'], axis=1)

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
#our_user = our_user.sort_values(by=['date'])
our_user.set_index('date', inplace=True)

outpath = path+select_participant+'/'

if not os.path.exists(outpath):
    os.mkdir(outpath)

#creating and writing out companion data:
def find_trendline(arr):
    x = np.arange(1,len(arr)+1)
    y = np.array(arr)
    z = np.polyfit(x,y,1)
    return z

our_user_outdata = pd.DataFrame(columns=['type','slope','y-intercept','first_predict', 'final_predict', 'improvement_percentage'])

print('creating companion data')
#speaking time data
dta = our_user['speaking_percentage'].to_numpy()
dta_line = find_trendline(dta)
our_user_outdata.at[0,'type'] = 'speaking_time'
our_user_outdata.at[0,'slope'] = dta_line[0]
our_user_outdata.at[0,'y-intercept'] = dta_line[1]
first_prediction = dta_line[1] + dta_line[0]
final_prediction = dta_line[1] + (dta_line[0]*our_user.shape[0])
improvement = (final_prediction/first_prediction)*100-100
our_user_outdata.at[0,'first_predict'] = first_prediction
our_user_outdata.at[0,'final_predict'] = final_prediction
our_user_outdata.at[0,'improvement_percentage'] = improvement


#interruptions data
dta = our_user['interruptions'].to_numpy()
dta_line = find_trendline(dta)
our_user_outdata.at[1,'type'] = 'interruptions'
our_user_outdata.at[1,'slope'] = dta_line[0]
our_user_outdata.at[1,'y-intercept'] = dta_line[1]
first_prediction = dta_line[1] + dta_line[0]
final_prediction = dta_line[1] + (dta_line[0]*our_user.shape[0])
improvement = (final_prediction/first_prediction)*100-100
our_user_outdata.at[1,'first_predict'] = first_prediction
our_user_outdata.at[1,'final_predict'] = final_prediction
our_user_outdata.at[1,'improvement_percentage'] = improvement


#affirmations data
dta = our_user['affirmations'].to_numpy()
dta_line = find_trendline(dta)
our_user_outdata.at[2,'type'] = 'affirmations'
our_user_outdata.at[2,'slope'] = dta_line[0]
our_user_outdata.at[2,'y-intercept'] = dta_line[1]
first_prediction = dta_line[1] + dta_line[0]
final_prediction = dta_line[1] + (dta_line[0]*our_user.shape[0])
improvement = (final_prediction/first_prediction)*100-100
our_user_outdata.at[2,'first_predict'] = first_prediction
our_user_outdata.at[2,'final_predict'] = final_prediction
our_user_outdata.at[2,'improvement_percentage'] = improvement


#influences data
dta = our_user['influenced'].to_numpy()
dta_line = find_trendline(dta)
our_user_outdata.at[3,'type'] = 'influences'
our_user_outdata.at[3,'slope'] = dta_line[0]
our_user_outdata.at[3,'y-intercept'] = dta_line[1]
first_prediction = dta_line[1] + dta_line[0]
final_prediction = dta_line[1] + (dta_line[0]*our_user.shape[0])
improvement = (final_prediction/first_prediction)*100-100
our_user_outdata.at[3,'first_predict'] = first_prediction
our_user_outdata.at[3,'final_predict'] = final_prediction
our_user_outdata.at[3,'improvement_percentage'] = improvement


our_user_outdata.to_csv(outpath +select_participant+'_data.csv')

#TODO: need to make these lines curvy instead of jagged

img_size = (7,4)

fig1 = plt.figure(figsize=img_size)
our_user['speaking_percentage'].plot(color = 'dodgerblue', linewidth=2.0, use_index=True, label='You')
our_user['ideal_speaking_time'].plot(kind='bar', color = 'chocolate', use_index=True, label='Ideal')
plt.xlabel('Meeting Date')
plt.ylabel('% Speaking Time')
plt.title('Ideal and Actual Percentage of Time Spoken per Meeting')
plt.legend(loc="best")
fig1.savefig(outpath+'speaking_percentage_user.png',bbox_inches='tight')
plt.close(fig1)


fig2 = plt.figure(figsize=img_size)
our_user['interruptions'].plot(color='firebrick',linewidth=2.0, use_index=True)
plt.xlabel('Meeting Date')
plt.ylabel('Interruptions')
plt.title('Interruptions over Time')
plt.xticks(rotation='vertical')
fig2.savefig(outpath+'interruptions_user.png',bbox_inches='tight')
plt.close(fig2)


fig3 = plt.figure(figsize=img_size)
our_user['affirmations'].plot(color='forestgreen',linewidth=2.0, use_index=True)
plt.xlabel('Meeting Date')
plt.ylabel('Affirmations')
plt.title('Affirmations over Time')
plt.xticks(rotation='vertical')
fig3.savefig(outpath+'affirmations_user.png',bbox_inches='tight')
plt.close(fig3)


#TODO: currently this shows the number of times they were influenced, not the other way around - needs to be fixed
fig4 = plt.figure(figsize=img_size)
our_user['influenced'].plot(color='gold',linewidth=2.0, use_index=True)
plt.xlabel('Meeting Date')
plt.ylabel('Influences')
plt.title('Influences over Time')
plt.xticks(rotation='vertical')
fig4.savefig(outpath+'influences_user.png',bbox_inches='tight')
plt.close(fig4)

print('first 4 plots complete')

#Now onto the boxplots
#pulling out all unique users
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
orderDF = pd.DataFrame(columns=['myindex','name','speaking_time_median','interruptions_median','affirmations_median','influences_median'])

u_counter = 0
for u in imp_users:
    #finding the data for each user and then creating a list of it, writing it to list of lists
    #the first user is always the target user, and so their median gets boosted so they always show up
    #on the graph first (this dosn't mess with the actual data, just the order in which they're presented)
    udf = all_meeting_data[all_meeting_data['participant']==u]
    sp_list = udf['speaking_percentage'].to_list()
    sp_med = statistics.median(sp_list)
    if u_counter == 0:
        sp_med = sp_med*100
    int_list = udf['interruptions'].to_list()
    int_med = statistics.median(int_list)
    if u_counter == 0:
        int_med = int_med*100
    aff_list = udf['affirmations'].to_list()
    aff_med = statistics.median(aff_list)
    if u_counter == 0:
        aff_med = aff_med*100
    inf_list = udf['influenced'].to_list()
    inf_med = statistics.median(inf_list)
    if u_counter == 0:
        inf_med = inf_med*100
    #now writing the data to appropriate storage
    speaking_time.append(sp_list)
    interruptions.append(int_list)
    affirmations.append(aff_list)
    influences.append(inf_list)
    orderDF.at[u_counter, 'myindex'] = u_counter
    if u_counter == 0:
        orderDF.at[u_counter, 'name'] = 'YOU!'
    else:
        orderDF.at[u_counter, 'name'] = known_users.get(u)
    orderDF.at[u_counter, 'speaking_time_median'] = sp_med
    orderDF.at[u_counter, 'interruptions_median'] = int_med
    orderDF.at[u_counter, 'affirmations_median'] = aff_med
    orderDF.at[u_counter, 'influences_median'] = inf_med
    u_counter += 1


#Reordering data based on the relevant medians
orderDF2 = orderDF.sort_values(by='speaking_time_median', ascending=False)
sp_order = orderDF2['myindex'].to_list()
sp_names = orderDF2['name'].to_list()
speaking_time2 = []
for item in sp_order:
    nextlist = speaking_time[item]
    speaking_time2.append(nextlist)



fig5 = plt.figure(1, figsize=img_size)
ax5 = fig5.add_subplot(111)
bp5 = ax5.boxplot(speaking_time2,patch_artist=True, meanline=True)
ax5.set_xticklabels(sp_names, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Speaking Time %')
plt.title('Distribution of Speaking Time by Teammate')
for box in bp5['boxes']:
    # change fill color
    box.set( facecolor = 'royalblue' )
## change color and linewidth of the medians
for mean in bp5['means']:
    mean.set(color='black', linewidth=2)
fig5.savefig(outpath+'speaking_time_group.png',bbox_inches='tight')
plt.close(fig5)


#Reordering data based on the relevant medians
orderDF2 = orderDF.sort_values(by='interruptions_median', ascending=False)
int_order = orderDF2['myindex'].to_list()
int_names = orderDF2['name'].to_list()
interruptions2 = []
for item in int_order:
    nextlist = interruptions[item]
    interruptions2.append(nextlist)


fig6 = plt.figure(1, figsize=img_size)
ax6 = fig6.add_subplot(111)
bp6 = ax6.boxplot(interruptions2,patch_artist=True, meanline=True)
ax6.set_xticklabels(int_names, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Interruptions')
plt.title('Distribution of Interruptions by Teammate')
for box in bp6['boxes']:
    # change fill color
    box.set( facecolor = 'firebrick' )
## change color and linewidth of the medians
for mean in bp6['means']:
    mean.set(color='black', linewidth=2)
fig6.savefig(outpath+'interruptions_group.png',bbox_inches='tight')
plt.close(fig6)


#Reordering data based on the relevant medians
orderDF2 = orderDF.sort_values(by='affirmations_median', ascending=False)
aff_order = orderDF2['myindex'].to_list()
aff_names = orderDF2['name'].to_list()
affirmations2 = []
for item in aff_order:
    nextlist = affirmations[item]
    affirmations2.append(nextlist)


fig7 = plt.figure(1, figsize=img_size)
ax7 = fig7.add_subplot(111)
bp7 = ax7.boxplot(affirmations2,patch_artist=True, meanline=True)
ax7.set_xticklabels(aff_names, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Affirmations')
plt.title('Distribution of Affirmations by Teammate')
for box in bp7['boxes']:
    # change fill color
    box.set( facecolor = 'forestgreen' )
## change color and linewidth of the medians
for mean in bp7['means']:
    mean.set(color='black', linewidth=2)
fig7.savefig(outpath+'affirmations_group.png',bbox_inches='tight')
plt.close(fig7)


#Reordering data based on the relevant medians
orderDF2 = orderDF.sort_values(by='influences_median', ascending=False)
inf_order = orderDF2['myindex'].to_list()
inf_names = orderDF2['name'].to_list()
influences2 = []
for item in inf_order:
    nextlist = influences[item]
    influences2.append(nextlist)


fig8 = plt.figure(1, figsize=img_size)
ax8 = fig8.add_subplot(111)
bp8 = ax8.boxplot(influences2,patch_artist=True, meanline=True)
ax8.set_xticklabels(inf_names, rotation='vertical')
plt.xlabel('Teammate')
plt.ylabel('Influences')
plt.title('Distribution of Influences by Teammate')
for box in bp8['boxes']:
    # change fill color
    box.set( facecolor = 'gold' )
## change color and linewidth of the medians
for mean in bp8['means']:
    mean.set(color='black', linewidth=2)
fig8.savefig(outpath+'influences_group.png',bbox_inches='tight')
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
