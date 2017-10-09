# -*- coding: utf-8 -*-


class Utils(object):
    """
    Tools set for datas.
    """
    @classmethod
    def strip_unused_cols(cls, data, *unused_cols):
        """
        Strip the unused columns of data frame.
        :param data(DataFrame): input data frame.
        :param unused_cols(array): unused columns
        :return: None
        """
        for unused_col in unused_cols:
            data.drop(unused_col, axis=1, inplace=True)

