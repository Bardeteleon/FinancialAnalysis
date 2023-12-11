
from copy import copy
import datetime
import tkinter
import tkinter.ttk
import matplotlib
import re
from typing import List
from EntryFilter import EntryFilter
from enum import Enum, auto
from TimeInterval import MonthInterval, TimeInterval, TimeIntervalVariants
from Types import InterpretedEntry, Tag
from VisualizeStatement import VisualizeStatement

class Direction(Enum):
    UP = auto()
    DOWN = auto()

class InteractiveOverviewTkinter():

    def __init__(self, interpreted_entries):

        self.initial_interval_variant = TimeIntervalVariants.MONTH

        self.master = tkinter.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.master.option_add("*font", "20")
        self.master.title("Financial Analysis")

        s = tkinter.ttk.Style()
        s.configure('.', font=('Helvetica', 20))

        VisualizeStatement.general_configuration()

        self.interpreted_entries = interpreted_entries
        self.add_zero_entry_each_month_with_all_tags()

        self.pie_intervals = self.get_available_pie_intervals(self.initial_interval_variant)
        self.interval_variants = [str(interval.name) for interval in TimeIntervalVariants]
        self.tags = [str(tag.name) for tag in Tag]
        self.overall_balance_type = "Overall Balance"
        self.balance_types = [self.overall_balance_type] + self.tags

        self.pie_interval_var = tkinter.StringVar(self.master)
        self.pie_interval_var.set(self.pie_intervals[-1])

        self.interval_variant_var = tkinter.StringVar(self.master)
        self.interval_variant_var.set(str(self.initial_interval_variant.name))

        self.balance_type_var = tkinter.StringVar(self.master)
        self.balance_type_var.set(self.balance_types[0])

        self.interaction_frame = tkinter.Frame(self.master)
        self.interaction_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.pie_interval_menu = tkinter.ttk.OptionMenu(self.interaction_frame, self.pie_interval_var, command=self.pie_interval_menu_cmd)
        self.pie_interval_menu.set_menu(self.pie_interval_var.get(), *self.pie_intervals)
        self.pie_interval_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

        self.interval_variant_menu = tkinter.ttk.OptionMenu(self.interaction_frame, self.interval_variant_var, command=self.interval_variant_menu_cmd)
        self.interval_variant_menu.set_menu(self.interval_variant_var.get(), *self.interval_variants)
        self.interval_variant_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

        self.balance_type_menu = tkinter.ttk.OptionMenu(self.interaction_frame, self.balance_type_var, command=self.balance_type_cmd)
        self.balance_type_menu.set_menu(self.balance_type_var.get(), *self.balance_types)
        self.balance_type_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

        self.fig_balance = VisualizeStatement.get_figure_balance_per_interval(self.interpreted_entries, self.get_interval_variant())
        self.fig_balance_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig_balance, self.master)
        self.fig_balance_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.fig_pies = VisualizeStatement.get_figure_positive_negative_tag_pies(self.interpreted_entries, self.get_pie_interval())
        self.fig_pies_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig_pies, self.master)
        self.fig_pies_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.master.bind('+', lambda event: self.interval_variant_menu_shift(Direction.UP))
        self.master.bind('-', lambda event: self.interval_variant_menu_shift(Direction.DOWN))
        self.master.bind('s', lambda event: self.balance_type_menu_shift(Direction.UP))
        self.master.bind('w', lambda event: self.balance_type_menu_shift(Direction.DOWN))
        self.master.bind('d', lambda event: self.pie_interval_menu_shift(Direction.UP))
        self.master.bind('a', lambda event: self.pie_interval_menu_shift(Direction.DOWN))

        self.master.state("zoomed")
        self.master.mainloop()

    def pie_interval_menu_cmd(self, choice):
        self.fig_pies.clear()
        self.fig_pies = VisualizeStatement.get_figure_positive_negative_tag_pies(self.interpreted_entries, self.get_pie_interval(), fig=self.fig_pies)
        self.fig_pies_canvas.draw_idle()

    def balance_type_cmd(self, choice):
        filtered_entries = self.interpreted_entries
        if self.balance_type_var.get() != self.overall_balance_type:
            filtered_entries = EntryFilter.tag(self.interpreted_entries, Tag[self.balance_type_var.get()])
        self.fig_balance.clear()
        self.fig_balance = VisualizeStatement.get_figure_balance_per_interval(filtered_entries, self.get_interval_variant(), fig=self.fig_balance)
        self.fig_balance_canvas.draw_idle()

    def interval_variant_menu_cmd(self, choice):
        self.pie_interval_var.set('')
        self.pie_intervals = self.get_available_pie_intervals(self.get_interval_variant())
        self.pie_interval_menu.set_menu(self.pie_intervals[-1], *self.pie_intervals)
        self.balance_type_cmd(choice)
        self.pie_interval_menu_cmd(choice)

    def pie_interval_menu_shift(self, direction : Direction):
        self.shift_curr_selection_of_menu(direction, self.pie_intervals, self.pie_interval_var)
        self.pie_interval_menu_cmd(None)
    
    def balance_type_menu_shift(self, direction : Direction):
        self.shift_curr_selection_of_menu(direction, self.balance_types, self.balance_type_var)
        self.balance_type_cmd(None)
    
    def interval_variant_menu_shift(self, direction : Direction):
        self.shift_curr_selection_of_menu(direction, self.interval_variants, self.interval_variant_var)
        self.interval_variant_menu_cmd(None)

    def get_available_pie_intervals(self, variant : TimeIntervalVariants) -> List[str]:
        pie_intervals = list(EntryFilter.balance_per_interval(self.interpreted_entries, variant).keys())
        pie_intervals = sorted(pie_intervals, key=lambda x: int(re.sub("\D", "", x)), reverse=False)
        return pie_intervals

    def get_interval_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants[self.interval_variant_var.get()]

    def get_pie_interval(self) -> TimeInterval:
        return TimeInterval.create_from_string(self.get_interval_variant(), self.pie_interval_var.get())

    def add_zero_entry_each_month_with_all_tags(self):
        all_tags = [tag for tag in Tag]
        added_zero_month = MonthInterval.from_string("0001-1")
        extended_entries = []
        for entry in self.interpreted_entries:
            curr_month = MonthInterval(entry.date)
            if curr_month != added_zero_month:
                added_zero_month = curr_month
                zero_entry = InterpretedEntry(date=entry.date, amount=0.0, tags=all_tags)
                extended_entries.append(zero_entry)
            extended_entries.append(entry)
        self.interpreted_entries = extended_entries

    def shift_curr_selection_of_menu(self, direction : Direction, menu_data : List[str], menu_var : tkinter.StringVar):
        curr_index : int = menu_data.index(menu_var.get())
        if direction == Direction.UP:
            curr_index += 1
        elif direction == Direction.DOWN:
            curr_index -=1
        if curr_index in range(len(menu_data)):
            menu_var.set(menu_data[curr_index])