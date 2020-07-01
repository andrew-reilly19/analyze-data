#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
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

#GT users
known_users = {'MLRP_207nuzZNLc8YvoV':'Alena','MLRP_b8eXeA6wOsLaTGZ':'Brian','MLRP_4Z6SeqiBce2rVZP':'Marc','MLRP_9QQIU5xv6Vbferb':'Jarred','MLRP_2lb2J9sL14bWiLr':'Tamara', 'MLRP_2tOntZytvl6j4a1':'Gina', 'MLRP_8kT5pkyD7bYIkm1':'Andrew'}
#known_users = {'MLRP_207nuzZNLc8YvoV':'One','MLRP_b8eXeA6wOsLaTGZ':'Two','MLRP_4Z6SeqiBce2rVZP':'Three','MLRP_9QQIU5xv6Vbferb':'Four','MLRP_2lb2J9sL14bWiLr':'Five', 'MLRP_2tOntZytvl6j4a1':'Six', 'MLRP_8kT5pkyD7bYIkm1':'Seven'}

#RiffAI users
#known_users = {'q94yeKPfA7Nf6kp8JQ69NFQ0rQw2':'Burcin', 'mGZGS6HsATg0nwArrRoXF9yYiuF3':'Andrew', 'G0DAHoX1U8hbz1IefV2Vq3TmOy72':'Beth', 'JUQuvggv76ctK1nJNOWvkkf3McT2':'Jordan', 'V4Kc1uN0pgP7oVhaDjcmp6swV2F3':'Mike'}


#helper functions

#add date function
def add_date(row):
    rowmeet = row['meeting']
    rowdate = meeting_info[meeting_info['meeting']==rowmeet].iloc[0]['real_start'].strftime("%B %-d")
    return(rowdate)

#add trim flag to help remove unnecessary time at beginning and end
def trim_utterance_prep(row):
    flag = 0
    mtg_info = meeting_info[meeting_info['meeting']==row['meeting']]
    if (row['startTime'] >= mtg_info.iloc[0]['real_start']) & (row['startTime'] <= mtg_info.iloc[0]['real_end']):
        flag = 1
    return flag

#add speaking percentage
def get_speaking_percentage(row, thisdf):
    thisdf2 = thisdf[thisdf['meeting']==row['meeting']]
    tot_utt_length = thisdf2.utterance_length.sum()
    user_SP = row['utterance_length']
    return (user_SP/tot_utt_length*100)

#find the trendline for an array of data
def find_trendline(arr):
    x = np.arange(1,len(arr)+1)
    y = np.array(arr)
    z = np.polyfit(x,y,1)
    return z

def create_list(string):
    strg = string.replace("[", "").replace("]", "").replace("'", "").replace(" ", "")
    #print(strg)
    try:
        strg = strg.split(',')
    except:
        strg = list(strg)
    #print(strg)
    return(strg)



#function to wrap everything together

def create_plots(select_participant):
    #select_participant = 'MLRP_207nuzZNLc8YvoV'
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

    #print("Ideal speaking times found")

    #trimming the meeting utterancews for later
    total_meeting_data = df[df.meeting.isin(p_meetings)]

    #creating participant interactions df & selected user influence data
    user_i_data = total_meeting_data[(total_meeting_data['interruptions']>0) | (total_meeting_data['affirmations']>0) | (total_meeting_data['influenced']>0)]
    user_i_data = user_i_data.drop(['_id','startTime','endTime','utterance_length'], axis=1)

    users = total_meeting_data.participant.unique()
    cur_user_dict = {}
    opp_user_dict = {}
    u_count = 0
    for u in users:
        cur_user_dict[u] = u_count
        opp_user_dict[u_count] = u
        u_count += 1

    interruptions_grid = np.zeros((len(users),len(users)))
    affirmations_grid = np.zeros((len(users),len(users)))
    influences_grid = np.zeros((len(users),len(users)))
    meeting_influences = np.zeros((len(users), len(p_meetings)))

    cur_meet_dict = {}
    m_count = 0
    for m in p_meetings:
        cur_meet_dict[m] = m_count
        m_count += 1


    for index, row in user_i_data.iterrows():
        this_user = cur_user_dict.get(row['participant'])
        if row['interruptions'] > 0:
            a_list = create_list(row['interrupts_users'])
            print
            for u in a_list:
                that_user = cur_user_dict.get(u)
                cur_val = interruptions_grid[this_user, that_user]
                interruptions_grid[this_user, that_user] = cur_val + 1
        if row['affirmations'] > 0:
            a_list = create_list(row['affirms_users'])
            for u in a_list:
                that_user = cur_user_dict.get(u)
                cur_val = affirmations_grid[this_user, that_user]
                affirmations_grid[this_user, that_user] = cur_val + 1
        if row['influenced'] > 0:
            a_list = create_list(row['influenced_by_users'])
            for u in a_list:
                that_user = cur_user_dict.get(u)
                that_meet = cur_meet_dict.get(row['meeting'])
                cur_val = influences_grid[that_user, this_user]
                #note - this is reversed to keep consistency in end product (that_user influences this_user, which is opposite the other two)
                influences_grid[that_user, this_user] = cur_val + 1
                meeting_influences[that_user, that_meet] = meeting_influences[that_user, that_meet] + 1


    #trimming overall meeting data
    #print("user interactions complete")
    total_meeting_data['trimflag'] = total_meeting_data.apply(lambda row: trim_utterance_prep(row), axis=1)
    trimmed_meeting_data = total_meeting_data[total_meeting_data['trimflag']==1]
    trimmed_meeting_data = trimmed_meeting_data.drop(['_id','trimflag','interrupts_users','affirms_users','influenced_by_users', 'startTime','endTime'], axis=1)

    #print("Utterances Trimmed")
    #Trimmed and aggregate meeting data here will be used for the rest of the plotting

    agg_meeting_data = trimmed_meeting_data.groupby(['participant','meeting']).sum().reset_index()
    agg_meeting_data['speaking_percentage'] = agg_meeting_data.apply(lambda row: (get_speaking_percentage(row, agg_meeting_data)), axis=1)

    #print("Finalizing dataframe")

    all_meeting_data = agg_meeting_data.merge(meeting_ideal, left_on='meeting',right_on='meeting1')
    all_meeting_data['date'] = all_meeting_data.apply(lambda row: add_date(row), axis=1)
    all_meeting_data = all_meeting_data.drop('meeting1', axis=1)


    #print("Producing plots")

    our_user = all_meeting_data[all_meeting_data['participant']==select_participant]
    our_user.set_index('meeting', inplace=True)
    #adding in the proper influences, found earlier:
    inf_user = cur_user_dict.get(select_participant)
    sp_infs = meeting_influences[inf_user]
    MI = {}
    for m in p_meetings:
        m_index = cur_meet_dict.get(m)
        MI[m] = sp_infs[m_index]

    actual_influences = pd.DataFrame(list(MI.items()), columns=['meeting1','influences'])
    actual_influences.set_index('meeting1', inplace=True)
    our_user = our_user.join(actual_influences, lsuffix='meeting', rsuffix='meeting1')

    #our_user = our_user.sort_values(by=['date'])
    our_user = our_user.set_index('date', append=True).reset_index(level=0)


    outpath = path+'user_plots/'+select_participant+'/'
    os.makedirs(outpath, exist_ok=True)

    #creating and writing out companion data:
    our_user_outdata = pd.DataFrame(columns=['type','slope','y-intercept','first_predict', 'final_predict', 'change_percentage'])

    #print('creating companion data')
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
    our_user_outdata.at[0,'change_percentage'] = improvement


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
    our_user_outdata.at[1,'change_percentage'] = improvement


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
    our_user_outdata.at[2,'change_percentage'] = improvement


    #influences data
    dta = our_user['influences'].to_numpy()
    dta_line = find_trendline(dta)
    our_user_outdata.at[3,'type'] = 'influences'
    our_user_outdata.at[3,'slope'] = dta_line[0]
    our_user_outdata.at[3,'y-intercept'] = dta_line[1]
    first_prediction = dta_line[1] + dta_line[0]
    final_prediction = dta_line[1] + (dta_line[0]*our_user.shape[0])
    improvement = (final_prediction/first_prediction)*100-100
    our_user_outdata.at[3,'first_predict'] = first_prediction
    our_user_outdata.at[3,'final_predict'] = final_prediction
    our_user_outdata.at[3,'change_percentage'] = improvement


    our_user_outdata.to_csv(outpath +select_participant+'_data.csv')

    #TODO: need to make these lines curvy instead of jagged

    img_size = (7,4)

    fig1 = plt.figure(figsize=img_size)
    our_user['speaking_percentage'].plot(color = 'dodgerblue', linewidth=2.0, use_index=True, label='You')
    our_user['ideal_speaking_time'].plot(kind='bar', color = 'lightslategrey', use_index=True, label='Balanced')
    plt.xlabel('Meeting Date')
    plt.ylabel('% Speaking Time')
    plt.title('Balanced and Actual Percentage of Time Spoken per Meeting')
    plt.legend(loc="best")
    plt.ylim(ymin=0)
    fig1.savefig(outpath+'speaking_percentage_user.png',bbox_inches='tight')
    plt.close(fig1)


    fig2 = plt.figure(figsize=img_size)
    our_user['interruptions'].plot(color='firebrick',linewidth=2.0, use_index=True)
    plt.xlabel('Meeting Date')
    plt.ylabel('Interruptions')
    plt.title('Interruptions over Time')
    plt.xticks(rotation='vertical')
    plt.ylim(ymin=0)
    fig2.savefig(outpath+'interruptions_user.png',bbox_inches='tight')
    plt.close(fig2)


    fig3 = plt.figure(figsize=img_size)
    our_user['affirmations'].plot(color='forestgreen',linewidth=2.0, use_index=True)
    plt.xlabel('Meeting Date')
    plt.ylabel('Affirmations')
    plt.title('Affirmations over Time')
    plt.xticks(rotation='vertical')
    plt.ylim(ymin=0)
    fig3.savefig(outpath+'affirmations_user.png',bbox_inches='tight')
    plt.close(fig3)


    fig4 = plt.figure(figsize=img_size)
    our_user['influences'].plot(color='mediumorchid',linewidth=2.0, use_index=True)
    plt.xlabel('Meeting Date')
    plt.ylabel('Influences')
    plt.title('Influences over Time')
    plt.xticks(rotation='vertical')
    plt.ylim(ymin=0)
    fig4.savefig(outpath+'influences_user.png',bbox_inches='tight')
    plt.close(fig4)

    #print('first 4 plots complete')

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
        #influences need to use the other data we scraped to be the times influencing someone else instead of just the times influenced
        usr = cur_user_dict.get(u)
        inf_list = meeting_influences[usr]
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
    ax5.set_ylim(bottom=0)
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
    ax6.set_ylim(bottom=0)
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
    ax7.set_ylim(bottom=0)
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
    ax8.set_ylim(bottom=0)
    plt.xlabel('Teammate')
    plt.ylabel('Influences')
    plt.title('Distribution of Influences by Teammate')
    for box in bp8['boxes']:
        # change fill color
        box.set( facecolor = 'mediumorchid' )
    ## change color and linewidth of the medians
    for mean in bp8['means']:
        mean.set(color='black', linewidth=2)
    fig8.savefig(outpath+'influences_group.png',bbox_inches='tight')
    plt.close(fig8)


    #now generating the 3 sets of pie charts on interactions for this user
    smaller_img_size = (3,3)
    explode = (0.1,0)

    our_user_index = cur_user_dict.get(select_participant)

    user_interrupted = interruptions_grid[our_user_index,:]
    most_interrupts = user_interrupted.max()
    other_interrupts = user_interrupted.sum() - most_interrupts
    plotdata9 = [most_interrupts, other_interrupts]
    o_user = np.where(user_interrupted == most_interrupts)[0]
    o_user = opp_user_dict.get(o_user[0])
    o_user = known_users.get(o_user)
    plotlabels9 = o_user, 'Others'
    colors = ('crimson','slategrey')
    fig9 = plt.figure(figsize=smaller_img_size)
    plt.pie(plotdata9, explode=explode, labels=plotlabels9, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('You were interrupted most by...')
    fig9.savefig(outpath+'pie_interrupted_by.png',bbox_inches='tight')
    plt.close(fig9)

    user_interrupts = interruptions_grid[:,our_user_index]
    most_interrupts = user_interrupts.max()
    other_interrupts = user_interrupts.sum() - most_interrupts
    plotdata10 = [most_interrupts, other_interrupts]
    o_user = np.where(user_interrupts == most_interrupts)[0]
    o_user = opp_user_dict.get(o_user[0])
    o_user = known_users.get(o_user)
    plotlabels10 = o_user, 'Others'
    colors = ('crimson','slategrey')
    fig10 = plt.figure(figsize=smaller_img_size)
    plt.pie(plotdata10, explode=explode, labels=plotlabels10, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Whom you interrupted the most...')
    fig10.savefig(outpath+'pie_most_interrupts.png',bbox_inches='tight')
    plt.close(fig10)


    user_affirmed = affirmations_grid[our_user_index,:]
    most_affirms = user_affirmed.max()
    other_affirms = user_affirmed.sum() - most_affirms
    plotdata11 = [most_affirms, other_affirms]
    o_user = np.where(user_affirmed == most_affirms)[0]
    o_user = opp_user_dict.get(o_user[0])
    o_user = known_users.get(o_user)
    plotlabels11 = o_user, 'Others'
    colors = ('mediumseagreen','slategrey')
    fig11 = plt.figure(figsize=smaller_img_size)
    plt.pie(plotdata11, explode=explode, labels=plotlabels11, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('You were affirmed most by...')
    fig11.savefig(outpath+'pie_affirmed_by.png',bbox_inches='tight')
    plt.close(fig11)

    user_affirms = affirmations_grid[:,our_user_index]
    most_affirms = user_affirms.max()
    other_affirms = user_affirms.sum() - most_affirms
    plotdata12 = [most_affirms, other_affirms]
    o_user = np.where(user_affirms == most_affirms)[0]
    o_user = opp_user_dict.get(o_user[0])
    o_user = known_users.get(o_user)
    plotlabels12 = o_user, 'Others'
    colors = ('mediumseagreen','slategrey')
    fig12 = plt.figure(figsize=smaller_img_size)
    plt.pie(plotdata12, explode=explode, labels=plotlabels12, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Whom you affirmed the most...')
    fig12.savefig(outpath+'pie_most_affirms.png',bbox_inches='tight')
    plt.close(fig12)


    user_influenced = influences_grid[our_user_index,:]
    most_influences = user_influenced.max()
    other_influences = user_influenced.sum() - most_influences
    plotdata13 = [most_influences, other_influences]
    o_user = np.where(user_influenced == most_influences)[0]
    o_user = opp_user_dict.get(o_user[0])
    o_user = known_users.get(o_user)
    plotlabels13 = o_user, 'Others'
    colors = ('mediumorchid','slategrey')
    fig13 = plt.figure(figsize=smaller_img_size)
    plt.pie(plotdata13, explode=explode, labels=plotlabels13, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('You were influenced most by...')
    fig13.savefig(outpath+'pie_influenced_by.png',bbox_inches='tight')
    plt.close(fig13)

    user_influences = influences_grid[:,our_user_index]
    most_influences = user_influences.max()
    other_influences = user_influences.sum() - most_influences
    plotdata14 = [most_influences, other_influences]
    o_user = np.where(user_influences == most_influences)[0]
    o_user = opp_user_dict.get(o_user[0])
    o_user = known_users.get(o_user)
    plotlabels14 = o_user, 'Others'
    colors = ('mediumorchid','slategrey')
    fig14 = plt.figure(figsize=smaller_img_size)
    plt.pie(plotdata14, explode=explode, labels=plotlabels14, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Whom you influenced the most...')
    fig14.savefig(outpath+'pie_most_influences.png',bbox_inches='tight')
    plt.close(fig14)

    #print('complete!')


count_users = 0
count_all_users = len(known_users)
for key in known_users:
    create_plots(select_participant = key)
    count_users += 1
    print(count_users, '/', count_all_users)

print("Done!")



