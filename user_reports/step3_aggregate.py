#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 09:45:30 2020

@author: andrew
"""

import pandas as pd
import numpy as np

path = '/Users/andrew/Desktop/Riff_Analytics_Internship/analyze-data/user_reports/'

df = pd.read_csv (path+'utterances_annotated.csv')
df['startTime'] =  pd.to_datetime(df['startTime'])
df['endTime'] =  pd.to_datetime(df['endTime'])
meetings = df.meeting.unique()
meetingdf = pd.DataFrame(meetings)

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
user_df = df[df['participant']=='V4Kc1uN0pgP7oVhaDjcmp6swV2F3']
#user_df.meeting.unique()

#functions to return basic info (meeting start_time, end_time, date, etc.)
#def meeting_date(meeting):


#def meeting_begin(meeting):


#def meeting_end(meeting):



for meeting in meetings:
    intermediateDF = df[df['meeting']==meeting]
