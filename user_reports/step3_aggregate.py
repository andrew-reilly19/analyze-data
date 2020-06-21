#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np
import datetime
import os

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

dfinit = pd.read_csv (path+'utterances_annotated.csv')
dfinit['startTime'] =  pd.to_datetime(dfinit['startTime'])
dfinit['endTime'] =  pd.to_datetime(dfinit['endTime'])
df = dfinit.sort_values(by=['startTime'])

print('loaded data')

'''
For aggregate meeting stats, filter overall df by utterances for one specific user
    - Amy D : jMZgnpJrX1QwAN0oUkYNme9kD4b2
    - Beth : GcOHEObyGzTShEOpSzma6VpzT2Q2
    - Mike : V4Kc1uN0pgP7oVhaDjcmp6swV2F3
    - John Doucette : FJwf8UtoqvRJ4jnAaqzV5hcfxAG3
    - Brec Hanson : i6T3a2s5WpPo1dxZaRmIJlkFn4m1
    - Jordan : SDzkCh0CetQsNw2gUZS5HPX2FCe2
'''
known_users = {'jMZgnpJrX1QwAN0oUkYNme9kD4b2':'Amy','GcOHEObyGzTShEOpSzma6VpzT2Q2':'Beth','V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike','FJwf8UtoqvRJ4jnAaqzV5hcfxAG3':'John','i6T3a2s5WpPo1dxZaRmIJlkFn4m1':'Brec','SDzkCh0CetQsNw2gUZS5HPX2FCe2':'Jordan'}

select_participant = 'jMZgnpJrX1QwAN0oUkYNme9kD4b2' #Amy

#only looking at meetings this participant was in
meetings = dfinit[dfinit['participant']==select_participant].meeting.unique()
meetingsdf = pd.DataFrame(meetings)

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

counter = 0
total_meet = len(meetings)
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
    counter += 1
    print(counter, ' / ', total_meet)

print('finalizing new dataframe...')

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


# week_meetingsdf_noUs.to_csv(outpath + 'week_none_aggregates.csv')
# month_meetingsdf_noUs.to_csv(outpath + 'month_none_aggregates.csv')
# week_meetingsdf_TC.to_csv(outpath + 'week_TC_aggregates.csv')
# month_meetingsdf_TC.to_csv(outpath + 'month_TC_aggregates.csv')
# week_meetingsdf_TP.to_csv(outpath + 'week_TP_aggregates.csv')
# month_meetingsdf_TP.to_csv(outpath + 'month_TP_aggregates.csv')

print("User data processed, beginning overall data processing")

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
    #meeting
    m_start = intermediateDF.startTime.min()
    m_end = intermediateDF.endTime.max()
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

#add number of users
def add_nusers(row, meetDF):
    meet = row['meeting']
    smallmeetDF = meetDF[meetDF['meeting']==meet]
    nusers = smallmeetDF.shape[0]
    if nusers == 2:
        return("2")
    if nusers<=4:
        return("3-4")
    if nusers<=7:
        return("5-7")
    if nusers>7:
        return("8+")

avg_meetingsdf2['users_in_meeting'] =  avg_meetingsdf2.apply(lambda row: add_nusers(row, avg_meetingsdf2), axis=1)

#user utterances divide by 60 (turn into minutes) and then get average by dividing by meeting mins
avg_meetingsdf2['avg_user_time'] =  avg_meetingsdf2.apply(lambda row: (row['utterance_length']/60)/row['meetinglength'], axis=1)
avg_meetingsdf2['interruption_avg'] =  avg_meetingsdf2.apply(lambda row: (row['interruption']/row['meetinglength']), axis=1)
avg_meetingsdf2['affirmation_avg'] =  avg_meetingsdf2.apply(lambda row: (row['affirmation']/row['meetinglength']), axis=1)
avg_meetingsdf2['influence_avg'] =  avg_meetingsdf2.apply(lambda row: (row['influenced']/row['meetinglength']), axis=1)

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

