from typing import List, Dict
from Types import *
import matplotlib.pyplot
import numpy
import datetime
import logging

class VisualizeStatement:

    @staticmethod
    def formated_date(date : datetime.date) -> str:
        return f"{date.year}-{date.month}"

    @staticmethod
    def draw_amounts(interpreted_entries : List[InterpretedEntry]):
        fig, ax = matplotlib.pyplot.subplots()
        x = range(len(interpreted_entries))
        y = [entry.amount for entry in interpreted_entries]
        y = numpy.cumsum(y)
        ax.plot(x, y)
        ax.plot(x, numpy.zeros(len(x)), color="r")
        matplotlib.pyplot.show()

    @staticmethod
    def draw_plus_minus_bar_per_month(interpreted_entries : List[InterpretedEntry]):

        balance_per_month : Dict[str, float] = {}
        for entry in interpreted_entries:
            month : str = VisualizeStatement.formated_date(entry.date)
            if month in balance_per_month:
                balance_per_month[month] += entry.amount
            else:
                balance_per_month[month] = entry.amount

        x = range(len(balance_per_month))
        matplotlib.pyplot.bar(x, balance_per_month.values(), tick_label=list(balance_per_month.keys()))
        matplotlib.pyplot.grid(visible=True)
        matplotlib.pyplot.xticks(rotation=90)

    @staticmethod
    def draw_cake_of_month(month : datetime.date, interpreted_entries : List[InterpretedEntry]):
        requested_month = VisualizeStatement.formated_date(month)
        balance_per_tag : Dict[Tag, float] = {}
        for entry in interpreted_entries:
            curr_month = VisualizeStatement.formated_date(entry.date)
            curr_tag = None
            if requested_month == curr_month:
                if len(entry.tags) == 1:
                    curr_tag = entry.tags[0]
                elif len(entry.tags) > 1:
                    logging.warning(f"Entry has more than one tag. Only using first one. {entry}")
                    curr_tag = entry.tags[0]
                if curr_tag in balance_per_tag:
                    balance_per_tag[curr_tag] += entry.amount
                else:
                    balance_per_tag[curr_tag] = entry.amount
        positive_balance_per_tag = {key:value for (key,value) in balance_per_tag.items() if value >= 0}
        negative_balance_per_tag = {key:abs(value) for (key,value) in balance_per_tag.items() if value < 0}
        sum_positive = numpy.sum(list(positive_balance_per_tag.values()))
        sum_negative = -numpy.sum(list(negative_balance_per_tag.values()))
        fig, axs = matplotlib.pyplot.subplots(1, 2)
        axs[0].set_title(f"Income (Sum: +{sum_positive})")
        axs[0].pie(positive_balance_per_tag.values(), labels=positive_balance_per_tag.keys())
        axs[1].set_title(f"Expenses (Sum: {sum_negative})")
        axs[1].pie(negative_balance_per_tag.values(), labels=negative_balance_per_tag.keys())
        fig.suptitle(f"{requested_month} (Sum: {sum_positive + sum_negative})")
    
    @staticmethod
    def show():
        matplotlib.pyplot.show()
                    
                
