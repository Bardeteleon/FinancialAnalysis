
import datetime
import tkinter
import matplotlib
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

        self.months = list(EntryFilter.balance_per_interval(interpreted_entries, TimeIntervalVariants.MONTH).keys())

        self.intervals = [str(interval.name) for interval in TimeIntervalVariants]

        self.month_var = tkinter.StringVar(self.master)
        self.month_var.set(self.months[-1])

        self.interval_var = tkinter.StringVar(self.master)
        self.interval_var.set(self.intervals[0])

        self.interaction_frame = tkinter.Frame(self.master)
        self.interaction_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.month_menu = tkinter.OptionMenu(self.interaction_frame, self.month_var, *self.months)
        self.month_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.interval_menu = tkinter.OptionMenu(self.interaction_frame, self.interval_var, *self.intervals, command=self.interval_menu_cmd)
        self.interval_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.confirm_button = tkinter.Button(self.interaction_frame, text="GO", command=self.confirm_button_cmd)
        self.confirm_button.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, MonthInterval.from_string(self.month_var.get()))
        self.fig_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, self.master)
        self.fig_canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=1)

        self.master.state("zoomed")
        self.master.mainloop()

    def confirm_button_cmd(self):
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, MonthInterval.from_string(self.month_var.get()), fig=self.fig)
        self.fig_canvas.draw_idle()

    def interval_menu_cmd(self, choice):
        selected_interval = TimeIntervalVariants[self.interval_var.get()]
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, MonthInterval.from_string(self.month_var.get()), selected_interval, fig=self.fig)
        self.fig_canvas.draw_idle()