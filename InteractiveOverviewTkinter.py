
from copy import copy
import datetime
import tkinter
import tkinter.ttk
import matplotlib
import re
import logging
from typing import Callable, Dict, List
from Config import Config
from EntryFilter import EntryFilter
from enum import Enum, auto
from TimeInterval import MonthInterval, TimeInterval, TimeIntervalVariants
from Types import InterpretedEntry
from VisualizeStatement import VisualizeStatement
from dateutil.relativedelta import relativedelta
from tagging.NewTag import Tag, UndefinedTag
from tagging.TagConfig import TagConfig

class Direction(Enum):
    UP = auto()
    DOWN = auto()

class InteractiveOverviewTkinter():

    def __init__(self, interpreted_entries : List[InterpretedEntry], config : Config, tag_config : TagConfig):

        self.__config : Config = config
        self.__tag_config : TagConfig = tag_config
        self.__interpreted_entries : List[InterpretedEntry] = interpreted_entries

        self.initial_interval_variant = TimeIntervalVariants.MONTH

        self.__all_tags : List[Tag] = []

        self.master = tkinter.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.master.option_add("*font", "20")
        self.master.title("Financial Analysis")

        self.ttk_style = tkinter.ttk.Style()
        self.ttk_style.configure('.', font=('Helvetica', 20))

        VisualizeStatement.general_configuration()

        self.__find_out_min_and_max_date()
        self.__fill_zero_entries_for_data_range()
        self.__fill_all_tags()

        self.pie_intervals = self.get_available_pie_intervals(self.initial_interval_variant)
        self.interval_variants = [str(interval.name) for interval in TimeIntervalVariants]
        self.balance_type_to_data : Dict[str, Callable] = {"Internal -> External" : lambda: EntryFilter.external_transactions(self.__interpreted_entries)}
        self.main_id = self.__config.accounts[0].transaction_iban
        self.main_name = self.__config.accounts[0].name
        for account in self.__config.accounts [1:]:
            self.balance_type_to_data[f"{self.main_name} -> {account.name}"] = lambda other_id=account.transaction_iban: EntryFilter.transactions(self.__interpreted_entries, self.main_id, other_id)
        for tag in self.__all_tags:
            self.balance_type_to_data[str(tag)] = lambda tag=tag: EntryFilter.tag(self.__interpreted_entries, tag)
        self.balance_type_to_data.pop(str(UndefinedTag))
        self.balance_type_to_data["Undefined External"] = lambda: EntryFilter.external_transactions(EntryFilter.undefined_transactions(self.__interpreted_entries))
        self.balance_types = list(self.balance_type_to_data.keys())

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

        self.fig_balance = VisualizeStatement.creat_default_figure()
        self.fig_balance_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig_balance, self.master)
        self.fig_balance_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.balance_type_cmd(None)

        self.fig_pies = VisualizeStatement.creat_default_figure()
        self.fig_pies_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig_pies, self.master)
        self.fig_pies_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.pie_interval_menu_cmd(None)

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
        self.fig_pies = VisualizeStatement.get_figure_positive_negative_tag_pies(
                                                EntryFilter.external_transactions(self.__interpreted_entries), 
                                                self.get_pie_interval(),
                                                self.__all_tags,
                                                fig=self.fig_pies)
        self.fig_pies_canvas.draw_idle()

    def balance_type_cmd(self, choice):
        get_entries = self.balance_type_to_data[self.balance_type_var.get()]
        self.fig_balance.clear()
        self.fig_balance = VisualizeStatement.get_figure_balance_per_interval(
                                                get_entries() + self.__zero_entries, 
                                                self.get_interval_variant(),
                                                self.__all_tags,
                                                fig=self.fig_balance)
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
        pie_intervals = list(EntryFilter.balance_per_interval(self.__interpreted_entries, variant).keys())
        pie_intervals = sorted(pie_intervals, key=lambda x: int(re.sub("\D", "", x)), reverse=False)
        return pie_intervals

    def get_interval_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants[self.interval_variant_var.get()]

    def get_pie_interval(self) -> TimeInterval:
        return TimeInterval.create_from_string(self.get_interval_variant(), self.pie_interval_var.get())

    def shift_curr_selection_of_menu(self, direction : Direction, menu_data : List[str], menu_var : tkinter.StringVar):
        curr_index : int = menu_data.index(menu_var.get())
        if direction == Direction.UP:
            curr_index += 1
        elif direction == Direction.DOWN:
            curr_index -=1
        if curr_index in range(len(menu_data)):
            menu_var.set(menu_data[curr_index])

    def __find_out_min_and_max_date(self):
        self.__entry_data_start_date = datetime.date(9999,1,1)
        self.__entry_data_end_date = datetime.date(1,1,1)
        for entry in self.__interpreted_entries:
            self.__entry_data_end_date = entry.date if entry.date > self.__entry_data_end_date else self.__entry_data_end_date
            self.__entry_data_start_date = entry.date if entry.date < self.__entry_data_start_date else self.__entry_data_start_date
    
    def __fill_zero_entries_for_data_range(self):
        one_month = relativedelta(months=1)
        self.__zero_entries : List[InterpretedEntry] = [InterpretedEntry(date=self.__entry_data_start_date, amount=0.0)]
        while self.__zero_entries[-1].date < (self.__entry_data_end_date-one_month):
            self.__zero_entries.append(InterpretedEntry(date=(self.__zero_entries[-1].date+one_month), amount=0.0))

    def __fill_all_tags(self):
        for tag in self.__tag_config.tag_definitions:
            for contained_tag in tag.tag.get_contained_tags():
                self.__all_tags.append(contained_tag)
        self.__all_tags.append(UndefinedTag)