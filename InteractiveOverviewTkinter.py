
import datetime
import tkinter
import tkinter.ttk
import matplotlib
from typing import List
from EntryFilter import EntryFilter
from TimeInterval import MonthInterval, TimeInterval, TimeIntervalVariants
from VisualizeStatement import VisualizeStatement


class InteractiveOverviewTkinter():

    def __init__(self, interpreted_entries):

        self.initial_interval_variant = TimeIntervalVariants.MONTH

        self.master = tkinter.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.master.option_add("*font", "20")
        self.master.title("Financial Analysis")

        s = tkinter.ttk.Style()
        s.configure('.', font=('Helvetica', 20))

        self.interpreted_entries = interpreted_entries

        self.pie_intervals = self.get_available_pie_intervals(self.initial_interval_variant)

        self.interval_variants = (str(interval.name) for interval in TimeIntervalVariants)

        self.pie_interval_var = tkinter.StringVar(self.master)
        self.pie_interval_var.set(self.pie_intervals[-1])

        self.interval_variant_var = tkinter.StringVar(self.master)
        self.interval_variant_var.set(str(self.initial_interval_variant.name))

        self.interaction_frame = tkinter.Frame(self.master)
        self.interaction_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.pie_interval_menu = tkinter.ttk.OptionMenu(self.interaction_frame, self.pie_interval_var, command=self.pie_interval_menu_cmd)
        self.pie_interval_menu.set_menu(self.pie_interval_var.get(), *self.pie_intervals)
        self.pie_interval_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.interval_variant_menu = tkinter.ttk.OptionMenu(self.interaction_frame, self.interval_variant_var, command=self.interval_variant_menu_cmd)
        self.interval_variant_menu.set_menu(self.interval_variant_var.get(), *self.interval_variants)
        self.interval_variant_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.get_pie_interval())
        self.fig_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, self.master)
        self.fig_canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=1)

        self.master.state("zoomed")
        self.master.mainloop()

    def pie_interval_menu_cmd(self, choice):
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.get_pie_interval(), fig=self.fig)
        self.fig_canvas.draw_idle()

    def interval_variant_menu_cmd(self, choice):
        self.pie_interval_var.set('')
        self.pie_intervals = self.get_available_pie_intervals(self.get_interval_variant())
        self.pie_interval_menu.set_menu(self.pie_intervals[-1], *self.pie_intervals)

        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.get_pie_interval(), fig=self.fig)
        self.fig_canvas.draw_idle()

    def get_available_pie_intervals(self, variant : TimeIntervalVariants) -> List[str]:
        return list(EntryFilter.balance_per_interval(self.interpreted_entries, variant).keys())

    def get_interval_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants[self.interval_variant_var.get()]

    def get_pie_interval(self) -> TimeInterval:
        return TimeInterval.from_string(self.get_interval_variant(), self.pie_interval_var.get())