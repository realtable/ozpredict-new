import collections
import csv
import pickle
import plotly.graph_objects as go
from plotly.colors import n_colors
import pandas as pd
import numpy as np

with open('electorates.csv') as f:
    raw_electorates = [{k: v for k, v in row.items()}
                       for row in csv.DictReader(f, skipinitialspace=True)]
with open('poll_shifts.p', 'rb') as f:
    raw_shifts = pickle.load(f)

electorates = {
    'LNPvALP': [],
    'LNPvALPkeys': [],
    'LNPvOTH': [],
    'LNPvOTHkeys': [],
    'notLNP': 0
}
for i in raw_electorates:
    if i['vs'].strip() == '':
        if i['party'].strip() == 'ALP':
            electorates['LNPvALP'].append(-float(i['margin'].strip()))
            electorates['LNPvALPkeys'].append(i['elec_state'].strip())
        elif i['party'].strip() in ['LIB', 'NAT', 'LNP']:
            electorates['LNPvALP'].append(float(i['margin'].strip()))
            electorates['LNPvALPkeys'].append(i['elec_state'].strip())
    else:
        if i['vs'].strip() == 'v ALP' or i['party'].strip() == 'ALP':
            electorates['notLNP'] += 1
        elif i['vs'].strip() in ['v LIB', 'v NAT', 'v LNP']:
            electorates['LNPvOTH'].append(-float(i['margin'].strip()))
            electorates['LNPvOTHkeys'].append(i['elec_state'].strip())
        else:
            electorates['LNPvOTH'].append(float(i['margin'].strip()))
            electorates['LNPvOTHkeys'].append(i['elec_state'].strip())
print('electorates:', electorates)

prev_result = 51.5  # for LNP
sum_2019, count_2019 = 0, 0
sum_rest, count_rest = 0, 0
for i in raw_shifts.values():
    for k, j in i.items():
        if k == 2019:
            sum_2019 += round(j - prev_result, 1)
            count_2019 += 1
        else:
            sum_rest += round(j - prev_result, 1)
            count_rest += 1
shifts = np.linspace(sum_rest/count_rest, sum_2019/count_2019, 11)
shift_pcts = [f'{i if i > 0 else ""}0%' for i in range(0, 11)]
print('shifts:', shifts)
print('percents (0% = good, 100% = 2019):', shift_pcts)

sd = 3.2  # taken from http://freerangestats.info/elections/oz-2019/index.html
runs_per_shift = 1000
num_direct_electorates = len(electorates['LNPvALP'])
num_indirect_electorates = sum(map(lambda x: x > 0, electorates['LNPvOTH']))

# ASSUMING
# - all polls are equally accurate
# - seats not between LNP and ALP stay the same

totals = []
new_direct_electorates = {}
errors = np.random.normal(0, sd, len(
    shifts) * runs_per_shift * num_direct_electorates)
for i in range(len(shifts)):
    for j in range(runs_per_shift):
        def l(k, x):
            return x + shifts[i] + errors[i * runs_per_shift * num_direct_electorates + j * num_direct_electorates + k]
        new_margins = list(
            map(l, range(len(electorates['LNPvALP'])), electorates['LNPvALP']))
        totals.append((
            sum(map(lambda x: x > 0, new_margins)),
            shift_pcts[i]
        ))
        for elec in [electorates['LNPvALPkeys'][i] for i in range(len(new_margins)) if electorates['LNPvALP'][i] * new_margins[i] < 0]:
            if (elec, shift_pcts[i]) not in new_direct_electorates:
                new_direct_electorates[(elec, shift_pcts[i])] = 0
            new_direct_electorates[(elec, shift_pcts[i])] += 1

totals_counted = collections.Counter(totals)
totals_by_pct = {}
fracs_by_pct = {}
for pct in shift_pcts:
    totals_by_pct[pct] = [totals_counted[(
        seats + num_indirect_electorates, pct)] for seats in range(60, 81)]
    total = sum(totals_by_pct[pct])
    fracs_by_pct[pct] = [i / total for i in totals_by_pct[pct]]

fracs_by_pct = np.rot90(list(fracs_by_pct.values()))
colors = n_colors('rgb(255, 255, 255)',
                  'rgb(75, 140, 48)', 30, colortype='rgb')
colors_by_pct = np.vectorize(lambda x: colors[round(x * 100)])(fracs_by_pct)

fig = go.Figure(data=[go.Table(
    header=dict(values=list(range(60, 81))),
    cells=dict(values=np.vectorize(lambda x: f'{round(x * 100)}%')(fracs_by_pct), fill_color=colors_by_pct))])
fig.update_layout(title=dict(text="Number of LNP seats won by chance (top row is 2019 inaccuracy, bottom row is normal inaccuracy)",
                             font=dict(color='black')))
fig.show()

# # value gives how often it flipped (out of all non-zero outcomes weighted by frequency of outcome)
# electorate_analysis = {}
# for k, v in new_direct_electorates.items():
#     if k[0] not in electorate_analysis:
#         electorate_analysis[k[0]] = {}
#     electorate_analysis[k[0]][k[1]] = round(v / runs_per_shift * 100, 2)
new_direct_electorates = {k: round(
    v / runs_per_shift * 100, 2) for k, v in new_direct_electorates.items()}

with open('electorate_changes.p', 'wb+') as f:
    pickle.dump(new_direct_electorates, f)
