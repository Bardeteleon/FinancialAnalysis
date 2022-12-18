
import datetime
import tkinter
import matplotlib
from typing import List
from EntryFilter import EntryFilter
from TimeInterval import MonthInterval, TimeIntervalVariants
from VisualizeStatement import VisualizeStatement


class InteractiveOverviewTkinter():

    def __init__(self, interpreted_entries):

        self.master = tkinter.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.master.option_add("*font", "20")
        self.master.title("Financial Analysis")

        self.interpreted_entries = interpreted_entries

        self.pie_intervals = self.get_available_pie_intervals(TimeIntervalVariants.MONTH)

        self.intervals = [str(interval.name) for interval in TimeIntervalVariants]

        self.pie_interval_var = tkinter.StringVar(self.master)
        self.pie_interval_var.set(self.pie_intervals[-1])

        self.interval_var = tkinter.StringVar(self.master)
        self.interval_var.set(self.intervals[0])

        self.interaction_frame = tkinter.Frame(self.master)
        self.interaction_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.pie_interval_menu = tkinter.OptionMenu(self.interaction_frame, self.pie_interval_var, *self.pie_intervals, command=self.pie_interval_menu_cmd)
        self.pie_interval_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.interval_menu = tkinter.OptionMenu(self.interaction_frame, self.interval_var, *self.intervals, command=self.interval_menu_cmd)
        self.interval_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, MonthInterval.from_string(self.pie_interval_var.get()))
        self.fig_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, self.master)
        self.fig_canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=1)

        self.master.state("zoomed")
        self.master.mainloop()

    def pie_interval_menu_cmd(self, choice):
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, MonthInterval.from_string(self.pie_interval_var.get()), self.get_base_interval(), fig=self.fig)
        self.fig_canvas.draw_idle()

    def interval_menu_cmd(self, choice):
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, MonthInterval.from_string(self.pie_interval_var.get()), self.get_base_interval(), fig=self.fig)
        self.fig_canvas.draw_idle()

    def get_available_pie_intervals(self, variant : TimeIntervalVariants) -> List[str]:
        return list(EntryFilter.balance_per_interval(self.interpreted_entries, variant).keys())

    def get_base_interval(self) -> TimeIntervalVariants:
        return TimeIntervalVariants[self.interval_var.get()]