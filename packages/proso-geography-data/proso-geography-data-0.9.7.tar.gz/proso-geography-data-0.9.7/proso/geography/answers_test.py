# -*- coding: utf-8 -*-
import unittest
import proso.geography.answers as answers
import os


class TestBasics(unittest.TestCase):

    def test_from_csv(self):
        data = answers.from_csv(
            answer_csv=os.environ['RESOURCES_DIR'] + '/answer.csv',
            answer_options_csv=os.environ['RESOURCES_DIR'] + '/answer_options.csv',
            answer_ab_values_csv=os.environ['RESOURCES_DIR'] + '/answer_ab_values.csv',
            ab_value_csv=os.environ['RESOURCES_DIR'] + '/ab_value.csv'
            )
        self.assertEqual(len(data), 2)
        options = sorted(list(data.head().options)[0])
        self.assertEqual(options, [99, 101, 106, 177])
        ab_values = sorted(list(data.head().ab_values)[0])
        self.assertEqual(ab_values, ['recommendation_by_additive_function'])
