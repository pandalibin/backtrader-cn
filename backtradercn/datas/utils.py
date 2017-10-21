# -*- coding: utf-8 -*-
import datetime


class Utils(object):
    """
    Tools set for datas.
    """
    # duration(year) of data got when initiate collection
    INITIAL_DATA_YEAR = 3
    DB_ADDR = 'localhost'

    @classmethod
    def strip_unused_cols(cls, data, *unused_cols):
        """
        Strip the unused columns of data frame.
        :param data(DataFrame): input data frame.
        :param unused_cols(array): unused columns
        :return: None
        """
        for unused_col in unused_cols:
            data = data.drop(unused_col, axis=1)

        return data

    @classmethod
    def parse_date(cls, date_string):
        return datetime.datetime.strptime(date_string, '%Y-%m-%d')
