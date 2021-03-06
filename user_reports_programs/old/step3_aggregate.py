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

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports_riffai/'

dfinit = pd.read_csv (path+'utterances_annotated_S2_complete_2sec.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])
df = dfinit.sort_values(by=['startTime'])

meeting_info = pd.read_csv(path+'meetings_processed.csv')
meeting_info['real_start'] = pd.to_datetime(meeting_info['real_start'])
meeting_info['real_end'] = pd.to_datetime(meeting_info['real_end'] )


mecheck = df.meeting.unique()
mecheck = np.array(mecheck)
mecheck = np.sort(mecheck)

#research1 = dfinit[dfinit['meeting']=='research-2']
#research1 = dfinit[dfinit['meeting']=='research-5']
research1 = dfinit[dfinit['meeting']=='research-10']
# mindate = research1.startTime.min()
# maxdate = research1.endTime.max()
# meet_length = maxdate-mindate
# meet_length = meet_length.total_seconds()

research1.shape[0]

research1 = research1.drop(['_id','startTime','endTime','meeting','affirms_user', 'interrupts_user','influenced_by_user'], axis=1)
research1 = research1.groupby(['participant']).sum()
research1 = research1.sort_values(by=['utterance_length'])



tot_utts = research1.utterance_length.sum()
research1['utterance_share'] = research1.apply(lambda row: (row['utterance_length']/tot_utts*100), axis=1)


users = research1.participant.unique()

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

#known_users = {'MLRP_207nuzZNLc8YvoV':'A','MLRP_b8eXeA6wOsLaTGZ':'B','MLRP_4Z6SeqiBce2rVZP':'M','MLRP_9QQIU5xv6Vbferb':'J'}

known_users = {}

select_participant = 'MLRP_207nuzZNLc8YvoV'

#only looking at meetings this participant was in
meetings = dfinit[dfinit['participant']==select_participant].meeting.unique()
meetingsdf = pd.DataFrame(meetings)


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

meetingsdf = pd.DataFrame(list_of_dicts)
meetingsdf.columns = ['meeting_name','meeting_length_mins','meeting_date','total_participants','SU_speaking_time','SU_interruptions','SU_affirmations','SU_influenced_by','SU_interrupted','SU_affirmed','SU_influences']


#creating output path
if select_participant in known_users:
    outpath = path + known_users.get(select_participant) + '/'
else:
    outpath = path + select_participant + ''

if not os.path.exists(outpath):
    os.mkdir(outpath)


#finding common users and outputting the 10 most common collaborators
common_users = pd.DataFrame(list(ap_dict.items()), columns=['user','shared_meetings'])
common_users = common_users[(common_users['user']!=select_participant) & (common_users['shared_meetings']>1)]
most_common_buddy = common_users[(common_users['shared_meetings']==common_users.shared_meetings.max())].iloc[0]['user']

top_collaborators = common_users.nlargest(10,['shared_meetings'])

def add_names(row):
    user_id = row['user']
    try:
        name = known_users.get(user_id)
    except:
        name = "na"
    return(name)

top_collaborators['names'] = top_collaborators.apply(lambda row: add_names(row), axis=1)
top_collaborators.to_csv(outpath + 'other_known_users.csv', index = None)


#now to get some comparisons for just meetings with the top collaborator (in Mike's data, this is Amy)

with_best_buddy = {}
without_best_buddy = {}

for meeting in meetings:
    intermediateDF = df[df['meeting']==meeting]
    meeting_users = intermediateDF.participant.unique()
    if most_common_buddy in meeting_users:
        with_best_buddy[meeting]=1
    else:
        without_best_buddy[meeting]=0

with_best_buddy = pd.DataFrame(list(with_best_buddy.items()), columns=['meeting1','with_top_collaborator'])
without_best_buddy = pd.DataFrame(list(without_best_buddy.items()), columns=['meeting1','with_top_collaborator'])

bb = pd.concat([with_best_buddy, without_best_buddy])
meetingsdf = meetingsdf.merge(bb, left_on="meeting_name", right_on="meeting1")
meetingsdf = meetingsdf.drop('meeting1', axis=1)

# df.to_csv(outpath + 'all_meetings_aggregates.csv', index = None)

print("aggregating by month/weeks")
#finally, creating one last document strictly meant for graphing purposes - these will be combined on
#a weekly basis and it will be utterances/min, etc. per week

date_meetingsdf = meetingsdf.drop('meeting_name', axis=1)
date_meetingsdf['meeting_date'] = pd.to_datetime(date_meetingsdf['meeting_date'])

def getweek(row):
    week = row['meeting_date'].strftime("%V")
    return(week)

def getmonth(row):
    month = row['meeting_date'].strftime("%m")
    return(month)

def getyear(row):
    year = row['meeting_date'].strftime("%Y")
    return(year)

def group_nusers(row):
    nusers = row['total_participants']
    if nusers == 2:
        return("2")
    if nusers<=4:
        return("3-4")
    if nusers<=7:
        return("5-7")
    if nusers>7:
        return("8+")

date_meetingsdf['meeting_week'] = date_meetingsdf.apply(lambda row: getweek(row), axis=1)
date_meetingsdf['meeting_month'] = date_meetingsdf.apply(lambda row: getmonth(row), axis=1)
date_meetingsdf['meeting_year'] = date_meetingsdf.apply(lambda row: getyear(row), axis=1)
date_meetingsdf['total_participants'] = date_meetingsdf.apply(lambda row: group_nusers(row), axis=1)

week_meetingsdf = date_meetingsdf.drop(['meeting_date', 'meeting_month'],axis=1)
month_meetingsdf = date_meetingsdf.drop(['meeting_date', 'meeting_week'],axis=1)

week_meetingsdf_noUs = week_meetingsdf.drop(['total_participants','with_top_collaborator'],axis=1)
month_meetingsdf_noUs = month_meetingsdf.drop(['total_participants','with_top_collaborator'],axis=1)

week_meetingsdf_TC = week_meetingsdf.drop(['total_participants'],axis=1)
month_meetingsdf_TC = month_meetingsdf.drop(['total_participants'],axis=1)

week_meetingsdf_TP = week_meetingsdf.drop(['with_top_collaborator'],axis=1)
month_meetingsdf_TP = month_meetingsdf.drop(['with_top_collaborator'],axis=1)


week_meetingsdf_noUs = week_meetingsdf_noUs.groupby(['meeting_year','meeting_week']).sum()
month_meetingsdf_noUs = month_meetingsdf_noUs.groupby(['meeting_year','meeting_month']).sum()

week_meetingsdf_TC = week_meetingsdf_TC.groupby(['meeting_year','meeting_week','with_top_collaborator']).sum()
month_meetingsdf_TC = month_meetingsdf_TC.groupby(['meeting_year','meeting_month','with_top_collaborator']).sum()

week_meetingsdf_TP = week_meetingsdf_TP.groupby(['meeting_year','meeting_week','total_participants']).sum()
month_meetingsdf_TP = month_meetingsdf_TP.groupby(['meeting_year','meeting_month', 'total_participants']).sum()


week_meetingsdf_noUs.to_csv(outpath + 'week_none_aggregates.csv')
month_meetingsdf_noUs.to_csv(outpath + 'month_none_aggregates.csv')
week_meetingsdf_TC.to_csv(outpath + 'week_TC_aggregates.csv')
month_meetingsdf_TC.to_csv(outpath + 'month_TC_aggregates.csv')
week_meetingsdf_TP.to_csv(outpath + 'week_TP_aggregates.csv')
month_meetingsdf_TP.to_csv(outpath + 'month_TP_aggregates.csv')

print("User data processed, beginning overall data processing")

print('done!')

