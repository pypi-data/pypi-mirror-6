# -*- coding: utf-8 -*-

"""
Basic functionality to work with answer data.
"""

from util import load_csv


def from_csv(answer_csv, answer_options_csv=None, answer_ab_values_csv=None, ab_value_csv=None):
    """
    Loads answer data from the given CSV files.

    Args:
        answer_csv (str):
            name of the file containing  answer data
        answer_options_csv (str, optional):
            name of the file containing answer_options data
        answer_ab_values_csv (str, optional):
            name of the file containing answer_ab_values data
        ab_value_csv (str):
            name of the file containing ab_value data

    Returns:
        pandas.DataFrame
    """
    answers = load_csv(answer_csv)
    if answer_options_csv:
        options_from_csv(answers, answer_options_csv)
    if ab_value_csv and answer_ab_values_csv:
        ab_values_from_csv(answers, ab_value_csv, answer_ab_values_csv)
    return answers


def ab_values_from_csv(answers, ab_value_csv, answer_ab_values_csv):
    """
    Loads A/B values to the answers data frame.
    WARNING: The function modifies the given dataframe!

    Args:
        answers (pandas.DataFrame):
            dataframe containing answer data
        ab_value_csv (str):
            name of the file containing ab_value data
        answer_ab_values_csv (str, optional):
            name of the file containing answer_ab_values data

    Returns:
        pandas.DataFrame
    """
    ab_values = load_csv(ab_value_csv)
    answer_ab_values = load_csv(answer_ab_values_csv)
    ab_values_dict = {}
    answer_ab_values_dict = {}
    for i, row in ab_values.iterrows():
        ab_values_dict[row['id']] = row['value']
    for i, row in answer_ab_values.iterrows():
        if row['answer'] not in answer_ab_values_dict:
            answer_ab_values_dict[row['answer']] = []
        answer_ab_values_dict[row['answer']].append(ab_values_dict[row['value']])
    answers['ab_values'] = answers['id'].map(lambda id: answer_ab_values_dict.get(id, []))
    return answers


def options_from_csv(answers, answer_options_csv):
    """
    Loads options to the answers data frame.
    WARNING: The function modifies the given dataframe!

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        answer_options_csv (str):
            name of the file containing answer_options data

    Returns:
        pandas.DataFrame
    """
    options = load_csv(answer_options_csv)
    options_dict = {}
    for i, row in options.iterrows():
        if row['answer'] not in options_dict:
            options_dict[row['answer']] = []
        options_dict[row['answer']].append(row['place'])
    answers['options'] = answers['id'].map(lambda id: options_dict.get(id, []))
    return answers
