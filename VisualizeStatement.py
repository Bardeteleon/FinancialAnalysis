from typing import List, Dict
from Types import *
import matplotlib.pyplot
import numpy
import datetime

class VisualizeStatement:

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

        def formated_date(date : datetime.date) -> str:
            return f"{date.year}-{date.month}"

        balance_per_month : Dict[str, float] = {}
        for entry in interpreted_entries:
            if formated_date(entry.date) in balance_per_month:
                balance_per_month[formated_date(entry.date)] += entry.amount
            else:
                balance_per_month[formated_date(entry.date)] = entry.amount

        x = range(len(balance_per_month))
        print(balance_per_month.keys())
        print(balance_per_month.values())
        matplotlib.pyplot.bar(x, balance_per_month.values(), tick_label=list(balance_per_month.keys()))
        matplotlib.pyplot.show()