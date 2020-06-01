"""
################################################################################
  analyze.interruptions.py
################################################################################

This module reproduces the participant interruptions over all meetings
    (before this was computed client-side)

=============== ================================================================
Created on      May 27, 2020
--------------- ----------------------------------------------------------------
author(s)       Andrew Reilly
--------------- ----------------------------------------------------------------
Copyright
=============== ================================================================
"""

# Standard library imports
import pprint
from datetime import datetime, timedelta

# Third-party imports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Local application imports
from riffdata.riffdata import Riffdata

def create_single_db(participantId, new_db_name):
    riffdata=Riffdata()
    riffdata.create_single_participant_db(participantId, new_db_name)

def drop_single_db(new_db_name):
    riffdata=Riffdata()
    riffdata.client.drop_database(new_db_name)

def clean_interrupt_DF(dataframe):
    def row_time_compare(row):
        starttime_object = row['startTime']
        endtime_object = row['endTime']
        timediff = endtime_object-starttime_object
        return(timediff.total_seconds())
    dataframe['length_seconds'] = dataframe.apply (lambda row: row_time_compare(row), axis=1)

def compile_interruptions(meeting_DF, utterance_DF, participant_Id):
    '''
    First two functions add interruptions to the data, next two add affirmations, and the final adds the datetime
    '''
    def annotate_interruptions(row, indiv_meetingDF):
        interruptFlag = 0
        if row['participant'] == participant_Id:
            if row['length_seconds'] >= 5:
                target_start = row['startTime']
                target_end = row['endTime']
                #3 conditions - A speaks while B is speaking, there is at least a second overlap, and B stops before A
                interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_start) & (indiv_meetingDF['endTime']-timedelta(seconds=1)>target_start) & (indiv_meetingDF['endTime']<target_end)]
                if interDF.shape[0] > 0:
                    interruptFlag = 1
        return(interruptFlag)

    def compile_interruptions_row(row, utterance_DF):
        meeting_name = row['Meeting']
        meeting_utterancesDF = utterance_DF[utterance_DF['meeting']==meeting_name]

        #filtering to only include utterances > 2 seconds (no affirmations - they should be done above this)
        # meeting_utterancesDF = meeting_utterancesDF[meeting_utterancesDF['length_seconds']>=2]

        #annotating in interruptions (adds 0 if not an interruption, and a 1 if it is an interruption)
        meeting_utterancesDF['interrupting'] = meeting_utterancesDF.apply (lambda row: annotate_interruptions(row, meeting_utterancesDF), axis=1)

        #getting meeting length - this can be done better by using the meeting_events collection
        meeting_start = meeting_utterancesDF['startTime'].min()
        meeting_length = meeting_utterancesDF['endTime'].max() - meeting_start
        meeting_length_mins = meeting_length.total_seconds()/60
        interruptions = meeting_utterancesDF['interrupting'].sum()

        #interruptions per minute
        interrupts_per_min = interruptions/meeting_length_mins
        return(interrupts_per_min)

    meeting_DF['interruptions_per_min'] = meeting_DF.apply(lambda row: compile_interruptions_row(row, utterance_DF), axis=1)

    def annotate_affirmations(row, indiv_meetingDF):
        affirmflag = 0
        if row['participant'] == participant_Id:
            if (row['length_seconds'] <= 2) & (row['length_seconds'] >= .25):
                target_start = row['startTime']
                target_end = row['endTime']
                #3 conditions - A speaks while B is speaking, there is at least a second overlap, and B stops before A
                interDF = indiv_meetingDF[(indiv_meetingDF['startTime']<target_start) & (indiv_meetingDF['endTime']>target_end)]
                if interDF.shape[0] > 0:
                    affirmflag = 1
        return(affirmflag)

    def compile_affirmations_row(row, utterance_DF):
        meeting_name = row['Meeting']
        meeting_utterancesDF = utterance_DF[utterance_DF['meeting']==meeting_name]

        #annotating in affirmations (adds 0 if not an affirmation, and a 1 if it is an affirmation)
        meeting_utterancesDF['affirming'] = meeting_utterancesDF.apply (lambda row: annotate_affirmations(row, meeting_utterancesDF), axis=1)

        #getting meeting length - this can be done better by using the meeting_events collection
        meeting_start = meeting_utterancesDF['startTime'].min()
        meeting_length = meeting_utterancesDF['endTime'].max() - meeting_start
        meeting_length_mins = meeting_length.total_seconds()/60
        affirmations = meeting_utterancesDF['affirming'].sum()

        #interruptions per minute
        affirms_per_min = affirmations/meeting_length_mins
        return(affirms_per_min)

    meeting_DF['affirmations_per_min'] = meeting_DF.apply(lambda row: compile_affirmations_row(row, utterance_DF), axis=1)

    #redundant, I know, but I can't think of a better way that will still be (relatively) fast:
    def add_datetime(row, utterance_DF):
        meeting_name = row['Meeting']
        meeting_utterancesDF = utterance_DF[utterance_DF['meeting']==meeting_name]
        meeting_start = meeting_utterancesDF['startTime'].min()
        return(meeting_start)

    meeting_DF['startTime'] = meeting_DF.apply(lambda row: add_datetime(row, utterance_DF), axis=1)

def average_interruptions_chart(participant_Id):
    riffdata = Riffdata()
    db_name = 'riff_one_interrupt'

    #creating the database
    create_single_db(participant_Id, db_name)
    interrupt_db = riffdata.client[db_name]

    #putting utterances into data frame
    utterances = interrupt_db.utterances.find({})
    utteranceDF = pd.DataFrame(list(utterances))
    utteranceDF = utteranceDF.drop(['volumes', '__v'], axis=1)
    clean_interrupt_DF(utteranceDF)

    #removing utterances less than 10 milliseconds
    #utteranceDF = utteranceDF[utteranceDF['length_seconds']>=.01]

    #getting list of meetings to analyze
    meetings = utteranceDF.meeting.unique()
    meetingsDF = pd.DataFrame(meetings)
    meetingsDF.columns = ['Meeting']
    compile_interruptions(meetingsDF, utteranceDF, participant_Id)
    meetingsDF = meetingsDF.sort_values(by=['startTime'])
    #print(meetingsDF.head(20))

    #making interruptions plot
    fig = plt.figure()
    plt.scatter(meetingsDF.startTime, meetingsDF.interruptions_per_min)
    plt.xlabel('Date')
    plt.ylabel('Interruptions per Min')
    fig.suptitle('Interruptions over time for participant: %s' %participant_Id)
    plt.savefig('interruptions.png')
    plt.clf()

    #making affirmations plot
    fig = plt.figure()
    plt.scatter(meetingsDF.startTime, meetingsDF.affirmations_per_min)
    plt.xlabel('Date')
    plt.ylabel('Affirmations per Min')
    fig.suptitle('Affirmations over time for participant: %s' %participant_Id)
    plt.savefig('affirmations.png')
    plt.clf()

    #dropping the database again
    drop_single_db(db_name)
