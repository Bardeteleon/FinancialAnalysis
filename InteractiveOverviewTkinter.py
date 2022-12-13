
import tkinter
import matplotlib
from EntryFilter import EntryFilter
from VisualizeStatement import VisualizeStatement


class InteractiveOverviewTkinter():

    def __init__(self, interpreted_entries):

        self.master = tkinter.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.master.option_add("*font", "20")
        self.master.title("Financial Analysis")

        self.interpreted_entries = interpreted_entries

        self.months = list(EntryFilter.balance_per_month(interpreted_entries).keys())

        self.month_var = tkinter.StringVar(self.master)
        self.month_var.set(self.months[-1])

        self.interaction_frame = tkinter.Frame(self.master)
        self.interaction_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.month_menu = tkinter.OptionMenu(self.interaction_frame, self.month_var, *self.months)
        self.month_menu.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.confirm_button = tkinter.Button(self.interaction_frame, text="GO", command=self.confirm_button_cmd)
        self.confirm_button.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)

        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.month_var.get())
        self.fig_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, self.master)
        self.fig_canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=1)

        self.master.state("zoomed")
        self.master.mainloop()

    def confirm_button_cmd(self):
        self.fig.clear()
        self.fig = VisualizeStatement.draw_overview(self.interpreted_entries, self.month_var.get(), self.fig)
        self.fig_canvas.draw_idle()