
import tkinter
import matplotlib
from EntryFilter import EntryFilter
from VisualizeStatement import VisualizeStatement


class InteractiveOverviewTkinter():

    def __init__(self, master, interpreted_entries):

        self.master = master        
        self.master.title("Financial Analysis")

        self.interpreted_entries = interpreted_entries

        self.months = list(EntryFilter.balance_per_month(interpreted_entries).keys())

        self.month_var = tkinter.StringVar(master)
        self.month_var.set(self.months[0])

        self.month_menu = tkinter.OptionMenu(master, self.month_var, *self.months)
        self.month_menu.pack(side=tkinter.TOP, fill=tkinter.X)

        self.confirm_button = tkinter.Button(master, text="GO", command=self.confirm_button_cmd)
        self.confirm_button.pack(side=tkinter.TOP, fill=tkinter.X)

        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.month_var.get())
        self.fig_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, self.master)
        self.fig_canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=1)

    def confirm_button_cmd(self):
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.month_var.get(), self.fig)
        self.fig_canvas.draw_idle()