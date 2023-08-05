#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
  -------------
 * Caitlin Rivers
 * [cmrivers@vbi.vt.edu](cmrivers@vbi.vt.edu)
  -------------
 I developed checkerboard plots as a companion to case tree plots. A
 checkerboard plot shows when cases in a cluster occurred or were
 diagnosed, without assuming how they are related.
'''
import epipy
import matplotlib.pyplot as plt
from datetime import timedelta
from itertools import cycle
import numpy as np

def checkerboard_plot(df, case_id, cluster_id, date_col, labels='on'):
    '''
    PARAMETERS
    ---------------------
    df = pandas dataframe of line listing
    case_id = unique identifier of the cases
    cluster_id = identifier for each cluster, e.g. FamilyA
    date_col = column of onset or report dates
    labels = accepts 'on' or 'off'. Labels the first and last case in the cluster with
            the unique case identifier.

    RETURNS
    ---------------------
    matplotlib figure and axis objects
    '''
    clusters = epipy.group_clusters(df, cluster_id, date_col)

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.xaxis_date()
    ax.set_aspect('auto')
    axprop = ax.axis()
    fig.autofmt_xdate()

    grpnames = [key for key, group in clusters if len(group) > 1]
    plt.ylim(1, len(grpnames))
    plt.yticks(np.arange(len(grpnames)), grpnames)

    xtog = timedelta(((4*axprop[1]-axprop[0])/axprop[1]), 0, 0)
    counter = 0
    cols = cycle([color for i, color in enumerate(plt.rcParams['axes.color_cycle'])])

    for key, group in clusters:
        if len(group) > 1:
            color = next(cols)
            casenums = [int(num) for num in group.index]
            iter_casenums = cycle(casenums)

            positions = []

            for casedate in group[date_col].order():
                curr_casenum = next(iter_casenums)

                x1 = casedate
                x2 = casedate + xtog
                positions.append(x2)

                y1 = np.array([counter, counter])
                y2 = y1 + 1

                plt.fill_between([x1, x2], y1, y2, color=color, alpha=.3)
                ypos = y1[0] + .5

                if curr_casenum == min(casenums) or curr_casenum == max(casenums):
                    textspot = x1 + timedelta((x2 - x1).days/2.0, 0, 0)
                    plt.text(textspot, ypos, curr_casenum, horizontalalignment='center',
                    verticalalignment='center')


            counter += 1

    return fig, ax