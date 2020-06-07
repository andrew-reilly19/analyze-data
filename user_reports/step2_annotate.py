#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

df = pd.read_csv (path+'new_utterances.csv')

df['Start_time'] =  pd.to_datetime(df['Start_time'], format='%H:%M:%S.%f')


meetings = df.Meeting_Name.unique()
df_out = pd.read_csv (path+'new_utterances.csv')

df_out['is_interruption'] = 0
df_out['interrupts_user'] = ""
df_out['is_affirmation'] = 0
df_out['affirms_user'] = ""
df_out['is_influence'] = 0
df_out['influences_user'] = ""

def annotate_interruption(row, indiv_meetingDF):
    interruptFlag = 0
    if row['length_seconds'] >= 5:
        target_start = row['startTime']
        target_end = row['endTime']
        #3 conditions - A speaks while B is speaking, there is at least a second overlap, and B stops before A
        interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_start) & (indiv_meetingDF['endTime']-timedelta(seconds=1)>target_start) & (indiv_meetingDF['endTime']<target_end)]
        if interDF.shape[0] > 0:
            interruptFlag = 1
    return(interruptFlag)


def overall_annotation_function(row):
    utterance_start = row['Start_time']
    utterance_end = row['End_time']
    meeting = row['Meeting_Name']
    ref_df = df[(df['Meeting_Name']==meeting) & (df['Start_time']]

df_out.apply(lambda row: overall_annotation_function(row), axis=1)

df.dtypes
