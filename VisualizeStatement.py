from collections import Counter
from statistics import mean, median
from typing import List, Dict
from TimeInterval import TimeInterval, TimeIntervalVariants
from Types import *
import matplotlib
import matplotlib.pyplot
import numpy
import datetime
import logging
import tkinter
import re
from EntryFilter import EntryFilter
from tagging.TagGroup import TagGroup

matplotlib.use("TkAgg")

class VisualizeStatement:

    @staticmethod
    def general_configuration():
        matplotlib.rc("font", size=12)
    
    @staticmethod
    def creat_default_figure():
        return matplotlib.pyplot.figure(layout="constrained")

    @staticmethod
    def draw_balance_summed(entries : List[InterpretedEntry], interval_variant : TimeIntervalVariants, all_tags : List[Tag], axes=None):
        if not axes:
            fig, axes = matplotlib.pyplot.subplots()
        balance_per_interval : Dict[str, float] = EntryFilter.balance_per_interval(entries, interval_variant)
        balance_per_interval = dict(sorted(balance_per_interval.items(), 
                                                key=lambda x: int(re.sub("\D", "", x[0])), 
                                                reverse=False))
        axes.plot(range(len(balance_per_interval.keys())), numpy.cumsum(list(balance_per_interval.values())),
                    color=VisualizeStatement.get_common_color(entries, all_tags))
        axes.grid(visible=True)
        axes.set_xticks(range(len(balance_per_interval.keys())))
        axes.set_xticklabels(list(balance_per_interval.keys()), rotation=90)

    @staticmethod
    def draw_balance_per_interval(interpreted_entries : List[InterpretedEntry], interval_variant : TimeIntervalVariants, all_tags : List[Tag], ax=None):
        balance_per_interval : Dict[str, float] = EntryFilter.balance_per_interval(interpreted_entries, interval_variant)
        balance_per_interval = dict(sorted(balance_per_interval.items(), 
                                                key=lambda x: int(re.sub("\D", "", x[0])), 
                                                reverse=False))
        mean_balance = round(mean(balance_per_interval.values()))
        median_balance = round(median(balance_per_interval.values()))
        x = range(len(balance_per_interval))
        if not ax:
            fig, ax = matplotlib.pyplot.subplots()
        ax.bar(x, balance_per_interval.values(), color=VisualizeStatement.get_common_color(interpreted_entries, all_tags))
        ax.plot(x, [mean_balance]*len(x), label=f"Mean: {mean_balance}", color="blue")
        ax.plot(x, [median_balance]*len(x), label=f"Median: {median_balance}", color="green")
        ax.grid(visible=True)
        ax.set_title(f"Sum: {round(sum(balance_per_interval.values()))}")
        ax.set_xticks(x)
        ax.set_xticklabels(list(balance_per_interval.keys()), rotation=90)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='upper right')

    @staticmethod
    def get_figure_balance_per_interval(interpreted_entries : List[InterpretedEntry], interval_variant : TimeIntervalVariants, all_tags : List[Tag], fig=None):
        if not fig:
            fig = VisualizeStatement.creat_default_figure()
        spec = fig.add_gridspec(1,1)
        ax0 = fig.add_subplot(spec[0,0])
        VisualizeStatement.draw_balance_per_interval(interpreted_entries, interval_variant, all_tags, ax0)
        return fig

    @staticmethod
    def get_figure_balance_summed(interpreted_entries : List[InterpretedEntry], interval_variant : TimeIntervalVariants, all_tags : List[Tag], fig=None):
        if not fig:
            fig = VisualizeStatement.creat_default_figure()
        spec = fig.add_gridspec(1,1)
        ax0 = fig.add_subplot(spec[0,0])
        VisualizeStatement.draw_balance_summed(interpreted_entries, interval_variant, all_tags, ax0)
        return fig

    @staticmethod
    def draw_tag_pie_per_interval(interval : TimeInterval, interpreted_entries : List[InterpretedEntry], all_tags : List[Tag], axs=None):
        balance_per_tag : Dict[TagGroup, float] = EntryFilter.balance_per_tag_of_interval(interpreted_entries, interval)
        balance_sum = numpy.sum(list(balance_per_tag.values()))
        balance_per_tag_sorted = dict(sorted(balance_per_tag.items(), key=lambda x: abs(x[1]), reverse=False))
        if not axs:
            fig, axs = matplotlib.pyplot.subplots()
        axs.set_title(f"Sum: {balance_sum}")
        axs.pie(numpy.abs(list(balance_per_tag_sorted.values())), 
                labels=balance_per_tag_sorted.keys(), 
                colors=VisualizeStatement.get_colors_for_tags(list(balance_per_tag_sorted.keys()), all_tags),
                startangle=90)
        handles, labels = axs.get_legend_handles_labels()
        axs.legend(handles[::-1], labels[::-1], loc='upper left')

    @staticmethod
    def get_figure_positive_negative_tag_pies(interpreted_entries : List[InterpretedEntry], interval : TimeInterval, all_tags : List[Tag], fig=None):
        if not fig:
            fig = VisualizeStatement.creat_default_figure()
        spec = fig.add_gridspec(1,2)
        ax1 = fig.add_subplot(spec[0,0])
        ax2 = fig.add_subplot(spec[0,1])
        positive_entries = EntryFilter.positive_amount(interpreted_entries)
        negative_entries = EntryFilter.negative_amount(interpreted_entries)
        VisualizeStatement.draw_tag_pie_per_interval(interval, positive_entries, all_tags, ax1)
        VisualizeStatement.draw_tag_pie_per_interval(interval, negative_entries, all_tags, ax2)
        return fig
    
    @staticmethod
    def show():
        matplotlib.pyplot.show()

    @staticmethod
    def generate_colors(n):
        """Generate a set of n colors with maximum contrast."""
        cmap = matplotlib.pyplot.cm.get_cmap('hsv', n)
        colors = cmap(range(n))
        return colors

    @staticmethod
    def get_colors_for_tags(tag_groups : List[TagGroup], all_tags : List[Tag]):
        resulting_colors = [VisualizeStatement.get_tag_group_color(tag_group, VisualizeStatement.get_tag_to_color_map(all_tags)) for tag_group in tag_groups]
        return resulting_colors

    @staticmethod
    def get_common_color(entries : List[InterpretedEntry], all_tags : List[Tag]):
        filtered_entries = EntryFilter.no_zero_amount(entries)
        found_tags = [tag for entry in filtered_entries for tag in entry.tags]
        if len(found_tags) > 0:
            counter = Counter(found_tags)
            max_index = list(counter.values()).index(max(counter.values()))
            most_frequent_tag = list(counter.keys())[max_index]
            return VisualizeStatement.get_tag_to_color_map(all_tags)[most_frequent_tag]
        else:
            None

    @staticmethod
    def get_tag_group_color(tag_group : TagGroup, tag_to_color_map):
        tag_group_colors = [tag_to_color_map[tag] for tag in tag_group]
        return sum(tag_group_colors) / len(tag_group_colors)

    @staticmethod 
    def get_tag_to_color_map(all_tags : List[Tag]):
        colors_for_all_tags = VisualizeStatement.generate_colors(len(all_tags))
        tag_to_color_map = dict(zip(all_tags, colors_for_all_tags))
        return tag_to_color_map
