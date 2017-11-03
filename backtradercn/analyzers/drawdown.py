# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt


__all__ = ['TimeDrawDown']


class TimeDrawDown(bt.TimeFrameAnalyzerBase):
    """
    This analyzer calculates trading system drawdowns on the chosen
    timeframe which can be different from the one used in the underlying data
    Params:

      - ``timeframe`` (default: ``None``)
        If ``None`` the ``timeframe`` of the 1st data in the system will be
        used

        Pass ``TimeFrame.NoTimeFrame`` to consider the entire dataset with no
        time constraints

      - ``compression`` (default: ``None``)

        Only used for sub-day timeframes to for example work on an hourly
        timeframe by specifying "TimeFrame.Minutes" and 60 as compression

        If ``None`` then the compression of the 1st data of the system will be
        used
      - *None*

      - ``fund`` (default: ``None``)

        If ``None`` the actual mode of the broker (fundmode - True/False) will
        be autodetected to decide if the returns are based on the total net
        asset value or on the fund value. See ``set_fundmode`` in the broker
        documentation

        Set it to ``True`` or ``False`` for a specific behavior

    Methods:

      - ``get_analysis``

        Returns a dictionary (with . notation support and subdctionaries) with
        drawdown stats as values, the following keys/attributes are available:

        - ``drawdown`` - drawdown value in 0.xx %
        - ``maxdrawdown`` - drawdown value in monetary units
        - ``maxdrawdownperiod`` - drawdown length

      - Those are available during runs as attributes
        - ``dd``
        - ``maxdd``
        - ``maxddlen``
    """

    params = (
        ('fund', None),
    )

    def start(self):
        super(TimeDrawDown, self).start()
        if self.p.fund is None:
            self._fundmode = self.strategy.broker.fundmode
        else:
            self._fundmode = self.p.fund
        self.dd = 0.0
        self.maxdd = 0.0
        self.maxddlen = 0
        self.peak = float('-inf')
        self.ddlen = 0
        self.tmpmaxdd = 0
        self.tmpmaxddlen = 0
        self.drawdown_points = []
        self.tmpdatetime = None

    def on_dt_over(self):

        if not self._fundmode:
            value = self.strategy.broker.getvalue()
        else:
            value = self.strategy.broker.fundvalue

        # update the maximum seen peak
        if value >= self.peak:
            self.peak = value
            self.ddlen = 0  # start of streak

            if self.tmpdatetime and self.tmpmaxdd and self.tmpmaxddlen:
                tmpdrawdown = dict(
                    datetime=self.tmpdatetime.date(),
                    drawdown=self.tmpmaxdd,
                    drawdownlen=self.tmpmaxddlen
                )
                self.drawdown_points.append(tmpdrawdown)

            self.tmpdatetime_updated = False
            self.tmpmaxdd = 0
            self.tmpmaxddlen = 0
            self.tmpdatetime = None

        # draw down period
        else:
            # calculate the current drawdown
            self.dd = dd = 100.0 * (self.peak - value) / self.peak
            self.ddlen += bool(dd)  # if peak == value -> dd = 0

            if not self.tmpdatetime_updated:
                self.tmpdatetime = self.strategy.datas[0].datetime
                self.tmpdatetime_updated = True

            self.tmpmaxdd = max(self.tmpmaxdd, dd)
            self.tmpmaxddlen += bool(self.dd)

            # update the maxdrawdown if needed
            self.maxdd = max(self.maxdd, dd)
            self.maxddlen = max(self.maxddlen, self.ddlen)

    def stop(self):
        self.rets['maxdrawdown'] = self.maxdd
        self.rets['maxdrawdownperiod'] = self.maxddlen
        self.rets['drawdownpoints'] = self.drawdown_points
