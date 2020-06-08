#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew

NOTE: This is not as needed anymore given that the filtering is now done in step 0

"""

import pandas as pd
import numpy as np

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

df = pd.read_csv (path+'all_utterances.csv')


meetings = df.Meeting_Name.unique()

#function to return the number of participants who were in a meeting
#NOTE: This takes a little while, it's checking 1200 meetings
def meeting_participants(meeting):
    meetingdf = df[df.Meeting_Name == meeting]
    users = meetingdf.Participant_ID.unique()
    print(len(users))
    return len(users)

one_user_meetings = []
for meeting in meetings:
    nusers = meeting_participants(meeting)
    if nusers == 1:
        df = df[df.Meeting_Name != meeting]


print(len(df.Meeting_Name.unique()))

df.to_csv(path + 'new_utterances.csv', index = None)
