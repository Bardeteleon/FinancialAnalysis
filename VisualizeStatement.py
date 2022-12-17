from typing import List, Dict
from TimeInterval import TimeInterval, TimeIntervalVariants
from Types import *
import matplotlib
import numpy
import datetime
import logging
import tkinter
from EntryFilter import EntryFilter

matplotlib.use("TkAgg")

class VisualizeStatement:

    @staticmethod
    def draw_amounts(interpreted_entries : List[InterpretedEntry]):
        fig, ax = matplotlib.pyplot.subplots()
        x = range(len(interpreted_entries))
        y = [entry.amount for entry in interpreted_entries]
        y = numpy.cumsum(y)
        ax.plot(x, y)
        ax.plot(x, numpy.zeros(len(x)), color="r")

    @staticmethod
    def draw_balance_per_interval(interpreted_entries : List[InterpretedEntry], interval : TimeIntervalVariants, ax=None):
        balance_per_interval : Dict[str, float] = EntryFilter.balance_per_interval(interpreted_entries, interval)
        x = range(len(balance_per_interval))
        if not ax:
            fig, ax = matplotlib.pyplot.subplots()
        ax.bar(x, balance_per_interval.values())
        ax.grid(visible=True)
        ax.set_xticks(x)
        ax.set_xticklabels(list(balance_per_interval.keys()), rotation=90)

    @staticmethod
    def draw_tag_pie(month : str, interpreted_entries : List[InterpretedEntry], axs=None):
        balance_per_tag : Dict[Tag, float] = EntryFilter.balance_per_tag_of_month(interpreted_entries, month)
        balance_sum = numpy.sum(list(balance_per_tag.values()))
        if not axs:
            fig, axs = matplotlib.pyplot.subplots()
        axs.set_title(f"Sum: {balance_sum}")
        axs.pie(numpy.abs(list(balance_per_tag.values())), labels=balance_per_tag.keys())

    @staticmethod
    def draw_overview(interpreted_entries : List[InterpretedEntry], interval : TimeInterval, fig=None):
        matplotlib.rc("font", size=12)
        if not fig:
            fig = matplotlib.pyplot.figure(layout="constrained")
        spec = fig.add_gridspec(2,2)
        ax0 = fig.add_subplot(spec[0,:])
        ax1 = fig.add_subplot(spec[1,0])
        ax2 = fig.add_subplot(spec[1,1])
        positive_entries = EntryFilter.positive_amount(interpreted_entries)
        negative_entries = EntryFilter.negative_amount(interpreted_entries)
        VisualizeStatement.draw_balance_per_interval(interpreted_entries, TimeIntervalVariants.QUARTER, ax0)
        VisualizeStatement.draw_tag_pie(interval.to_string(), positive_entries, ax1)
        VisualizeStatement.draw_tag_pie(interval.to_string(), negative_entries, ax2)
        return fig
    
    @staticmethod
    def show():
        matplotlib.pyplot.show()
