
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
from EntryMapping import EntryMapping
from TimeInterval import MonthInterval, TimeInterval, TimeIntervalVariants
from Types import InterpretedEntry
from VisualizeStatement import VisualizeStatement
from dateutil.relativedelta import relativedelta
from tagging.Tag import Tag, UndefinedTag
from tagging.TagConfig import TagConfig

class Direction(Enum):
    UP = auto()
    DOWN = auto()

class BalanceVariant(Enum):
    PER_INTERVAL = auto()
    SUMMED = auto()

class InteractiveOverviewTkinter():

    def __init__(self, interpreted_entries : List[InterpretedEntry], config : Config, tag_config : TagConfig):

        self.__config : Config = config
        self.__tag_config : TagConfig = tag_config
        self.__interpreted_entries : List[InterpretedEntry] = interpreted_entries

        self.__initial_time_interval_variant = TimeIntervalVariants.MONTH

        VisualizeStatement.general_configuration()

        self.__find_out_min_and_max_date()
        self.__fill_zero_entries_for_data_range()
        self.__fill_all_tags()

        self.__init_tk_master()
        self.__init_ttk_style()
        self.__init_menu_items()
        self.__init_tk_option_menus()
        self.__init_tk_figure_canvas_for_matplotlib()
        self.__init_keyboard_shortcuts()

        self.__start_gui()

    def __init_tk_master(self):
        self.__master = tkinter.Tk()
        self.__master.protocol("WM_DELETE_WINDOW", self.__master.quit)
        self.__master.option_add("*font", "20")
        self.__master.title("Financial Analysis")

    def __init_ttk_style(self):
        self.__ttk_style = tkinter.ttk.Style()
        self.__ttk_style.configure('.', font=('Helvetica', 20))

    def __init_menu_items(self):
        self.__time_intervals = self.__get_available_time_intervals(self.__initial_time_interval_variant)
        self.__time_interval_variants = [str(interval.name) for interval in TimeIntervalVariants]
        self.__balance_type_to_data : Dict[str, Callable] = {}
        self.__init_balance_menu_items_from_custom_balance_config()
        self.__init_balance_menu_items_with_general_info()
        self.__init_balance_menu_items_with_internal_accounts()
        self.__init_balance_menu_items_with_internal_account_transactions()
        self.__init_balance_menu_items_with_tags()
        self.__balance_types = list(self.__balance_type_to_data.keys())
        self.__balance_variants = [str(variant.name) for variant in BalanceVariant]

    def __init_balance_menu_items_from_custom_balance_config(self):
        if self.__config.custom_balances:
            for custom_balance in self.__config.custom_balances:
                self.__balance_type_to_data[custom_balance.name] = \
                    lambda custom_balance=custom_balance: EntryFilter.custom_balance(self.__balance_type_to_data, custom_balance)

    def __init_balance_menu_items_with_internal_accounts(self):
        account_index_to_id = EntryMapping.account_index_to_id(self.__interpreted_entries)
        for account_idx, account in enumerate(self.__config.internal_accounts):
            if account_idx in account_index_to_id.keys():
                self.__balance_type_to_data[f"{account.name} (with input)"] = \
                    lambda main_id=account_index_to_id[account_idx]: \
                        EntryFilter.account(self.__interpreted_entries, main_id)
            else:
                self.__balance_type_to_data[f"{account.name} (by transactions)"] = \
                    lambda other_id=account.transaction_iban: \
                        EntryFilter.reverse_sign_of_amounts(
                            EntryFilter.transactions(self.__interpreted_entries, None, other_id))
                    
    def __init_balance_menu_items_with_internal_account_transactions(self):
        self.__main_id = self.__config.internal_accounts[0].transaction_iban
        self.__main_name = self.__config.internal_accounts[0].name
        for account in self.__config.internal_accounts[1:]:
            self.__balance_type_to_data[f"{self.__main_name} -> {account.name}"] = \
                lambda other_id=account.transaction_iban: EntryFilter.transactions(self.__interpreted_entries, self.__main_id, other_id)

    def __init_balance_menu_items_with_tags(self):
        for tag in self.__all_tags:
            self.__balance_type_to_data[str(tag)] = lambda tag=tag: EntryFilter.tag(self.__interpreted_entries, tag)
        self.__balance_type_to_data.pop(str(UndefinedTag))

    def __init_balance_menu_items_with_general_info(self):
        self.__balance_type_to_data["Internal -> External"] = \
            lambda: EntryFilter.external_transactions(self.__interpreted_entries)
        self.__balance_type_to_data["Undefined External"] = \
            lambda: EntryFilter.external_transactions(EntryFilter.undefined_transactions(self.__interpreted_entries))

    def __init_tk_option_menus(self):
        self.__time_interval_var = tkinter.StringVar(self.__master)
        self.__time_interval_var.set(self.__time_intervals[-1])

        self.__time_interval_variant_var = tkinter.StringVar(self.__master)
        self.__time_interval_variant_var.set(str(self.__initial_time_interval_variant.name))

        self.__balance_type_var = tkinter.StringVar(self.__master)
        self.__balance_type_var.set(self.__balance_types[0])

        self.__balance_variant_var = tkinter.StringVar(self.__master)
        self.__balance_variant_var.set(self.__balance_variants[0])

        self.__interaction_frame = tkinter.Frame(self.__master)
        self.__interaction_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.__time_interval_menu = tkinter.ttk.OptionMenu(self.__interaction_frame, self.__time_interval_var, command=self.__time_interval_menu_cmd)
        self.__time_interval_menu.set_menu(self.__time_interval_var.get(), *self.__time_intervals)
        self.__time_interval_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

        self.__time_interval_variant_menu = tkinter.ttk.OptionMenu(self.__interaction_frame, self.__time_interval_variant_var, command=self.__time_interval_variant_menu_cmd)
        self.__time_interval_variant_menu.set_menu(self.__time_interval_variant_var.get(), *self.__time_interval_variants)
        self.__time_interval_variant_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

        self.__balance_type_menu = tkinter.ttk.OptionMenu(self.__interaction_frame, self.__balance_type_var, command=self.__balance_type_cmd)
        self.__balance_type_menu.set_menu(self.__balance_type_var.get(), *self.__balance_types)
        self.__balance_type_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

        self.__balance_variant_menu = tkinter.ttk.OptionMenu(self.__interaction_frame, self.__balance_variant_var, command=self.__balance_variant_cmd)
        self.__balance_variant_menu.set_menu(self.__balance_variant_var.get(), *self.__balance_variants)
        self.__balance_variant_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)

    def __init_tk_figure_canvas_for_matplotlib(self):
        self.__fig_balance = VisualizeStatement.creat_default_figure()
        self.__fig_balance_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.__fig_balance, self.__master)
        self.__fig_balance_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.__balance_type_cmd(None)

        self.__fig_pies = VisualizeStatement.creat_default_figure()
        self.__fig_pies_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.__fig_pies, self.__master)
        self.__fig_pies_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.__time_interval_menu_cmd(None)

    def __init_keyboard_shortcuts(self):
        self.__master.bind('+', lambda event: self.__time_interval_variant_menu_shift(Direction.UP))
        self.__master.bind('-', lambda event: self.__time_interval_variant_menu_shift(Direction.DOWN))
        self.__master.bind('s', lambda event: self.__balance_type_menu_shift(Direction.UP))
        self.__master.bind('w', lambda event: self.__balance_type_menu_shift(Direction.DOWN))
        self.__master.bind('d', lambda event: self.__time_interval_menu_shift(Direction.UP))
        self.__master.bind('a', lambda event: self.__time_interval_menu_shift(Direction.DOWN))
        self.__master.bind('q', lambda event: self.__balance_variant_menu_shift(Direction.UP))
    
    def __start_gui(self):
        self.__master.state("zoomed")
        self.__master.mainloop()

    def __time_interval_menu_cmd(self, choice):
        if self.__balance_variant_var.get() == BalanceVariant.SUMMED.name:
            selected_visualize_statement_function = VisualizeStatement.get_figure_summed_account_balance_pie
        else:
            selected_visualize_statement_function = VisualizeStatement.get_figure_positive_negative_tag_pies
        self.__fig_pies.clear()
        self.__fig_pies = selected_visualize_statement_function(
                                                self.__interpreted_entries, 
                                                self.__get_time_interval(),
                                                self.__all_tags,
                                                self.__config.internal_accounts,
                                                fig=self.__fig_pies)
        self.__fig_pies_canvas.draw_idle()

    def __balance_type_cmd(self, choice):
        if self.__balance_variant_var.get() == BalanceVariant.SUMMED.name:
            selected_visualize_statement_function = VisualizeStatement.get_figure_balance_summed
        else:
            selected_visualize_statement_function = VisualizeStatement.get_figure_balance_per_interval
        get_entries = self.__balance_type_to_data[self.__balance_type_var.get()]
        self.__fig_balance.clear()
        self.__fig_balance = selected_visualize_statement_function(
                                                get_entries() + self.__zero_entries, 
                                                self.__get_time_interval_variant(),
                                                self.__all_tags,
                                                fig=self.__fig_balance) 
        self.__fig_balance_canvas.draw_idle()

    def __time_interval_variant_menu_cmd(self, choice):
        self.__time_interval_var.set('')
        self.__time_intervals = self.__get_available_time_intervals(self.__get_time_interval_variant())
        self.__time_interval_menu.set_menu(self.__time_intervals[-1], *self.__time_intervals)
        self.__balance_type_cmd(choice)
        self.__time_interval_menu_cmd(choice)
    
    def __balance_variant_cmd(self, choice):
        self.__balance_type_cmd(choice)
        self.__time_interval_menu_cmd(choice)

    def __time_interval_menu_shift(self, direction : Direction):
        self.__shift_curr_selection_of_menu(direction, self.__time_intervals, self.__time_interval_var)
        self.__time_interval_menu_cmd(None)
    
    def __time_interval_variant_menu_shift(self, direction : Direction):
        self.__shift_curr_selection_of_menu(direction, self.__time_interval_variants, self.__time_interval_variant_var)
        self.__time_interval_variant_menu_cmd(None)
    
    def __balance_type_menu_shift(self, direction : Direction):
        self.__shift_curr_selection_of_menu(direction, self.__balance_types, self.__balance_type_var)
        self.__balance_type_cmd(None)
    
    def __balance_variant_menu_shift(self, direction : Direction):
        self.__shift_curr_selection_of_menu(direction, self.__balance_variants, self.__balance_variant_var)
        self.__balance_variant_cmd(None)

    def __get_available_time_intervals(self, variant : TimeIntervalVariants) -> List[str]:
        time_intervals = list(EntryMapping.balance_per_interval(self.__interpreted_entries, variant).keys())
        time_intervals = sorted(time_intervals, key=lambda x: int(re.sub("\D", "", x)), reverse=False)
        return time_intervals

    def __get_time_interval_variant(self) -> TimeIntervalVariants:
        return TimeIntervalVariants[self.__time_interval_variant_var.get()]

    def __get_time_interval(self) -> TimeInterval:
        return TimeInterval.create_from_string(self.__get_time_interval_variant(), self.__time_interval_var.get())

    def __shift_curr_selection_of_menu(self, direction : Direction, menu_data : List[str], menu_var : tkinter.StringVar):
        curr_index : int = menu_data.index(menu_var.get())
        if direction == Direction.UP:
            curr_index += 1
        elif direction == Direction.DOWN:
            curr_index -=1
        menu_var.set(menu_data[curr_index % len(menu_data)])

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
        self.__all_tags : List[Tag] = []
        for tag_definition in self.__tag_config.tag_definitions:
            for contained_tag in tag_definition.tag.get_contained_tags():
                self.__all_tags.append(contained_tag)
        self.__all_tags.append(UndefinedTag)