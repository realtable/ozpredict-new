import collections
import csv
import pickle
import plotly.express as px
import pandas as pd
import numpy as np

with open('electorates.csv') as f:
    raw_electorates = [{k: v for k, v in row.items()}
                       for row in csv.DictReader(f, skipinitialspace=True)]
with open('poll_shifts.p', 'rb') as f:
    raw_shifts = pickle.load(f)

electorates = {
    'LNPvALP': [],
    'LNPvOTH': [],
    'notLNP': 0
}
for i in raw_electorates:
    if i['vs'].strip() == '':
        if i['party'].strip() == 'ALP':
            electorates['LNPvALP'].append(-float(i['margin'].strip()))
        elif i['party'].strip() in ['LIB', 'NAT', 'LNP']:
            electorates['LNPvALP'].append(float(i['margin'].strip()))
    else:
        if i['vs'].strip() == 'v ALP' or i['party'] == 'ALP':
            electorates['notLNP'] += 1
        elif i['vs'].strip() in ['v LIB', 'v NAT', 'v LNP']:
            electorates['LNPvOTH'].append(-float(i['margin'].strip()))
        else:
            electorates['LNPvOTH'].append(float(i['margin'].strip()))
print('electorates:', electorates)

prev_result = 51.5  # for LNP
shift_years = []
shifts = []
year_names = {
    'simple': 'good',
    2013: 'like 2013',
    2016: 'like 2016',
    2019: 'like 2019'
}
for i in raw_shifts.values():
    for k, j in i.items():
        if k in year_names:
            shift_years.append(year_names[k])
            shifts.append(round(j - prev_result, 1))
print('shifts:', shifts)
print('years: ', shift_years)

sd = 3.2  # taken from http://freerangestats.info/elections/oz-2019/index.html
runs_per_shift = 500
num_direct_electorates = len(electorates['LNPvALP'])
num_indirect_electorates = sum(map(lambda x: x > 0, electorates['LNPvOTH']))

# ASSUMING
# - all polls are equally accurate
# - seats not between LNP and ALP stay the same

totals = []
errors = np.random.normal(0, sd, len(
    shifts) * runs_per_shift * num_direct_electorates)
for i in range(len(shifts)):
    for j in range(runs_per_shift):
        def l(k, x):
            return x + shifts[i] + errors[i * runs_per_shift * num_direct_electorates + j * num_direct_electorates + k] > 0
        totals.append((
            sum(map(
                l, range(len(electorates['LNPvALP'])), electorates['LNPvALP'])),
            shift_years[i]
        ))

totals_counted = collections.Counter(totals)
totals_by_type = pd.DataFrame({
    'seats': list(map(lambda x: x[0], totals_counted.keys())),
    'year': list(map(lambda x: x[1], totals_counted.keys())),
    'outcomes': totals_counted.values()
})
fig = px.bar(x=totals_by_type['seats'].values, y=totals_by_type['outcomes'].values,
             color=totals_by_type['year'].values, labels={'color': 'If poll accuracy is:'})

# fig.add_annotation(x=69.5, y=0, ayref='y',
#                    ax=0, ay=sum(totals_by_type[totals_by_type['seats'] == 70]['outcomes'].values),
#                    text='Past this point, parties will have to fight to form minority government',
#                    showarrow=True, arrowhead=0)
# fig.add_annotation(x=75.5, y=0, ayref='y',
#                    ax=0, ay=sum(totals_by_type[totals_by_type['seats'] == 76]['outcomes'].values),
#                    text='Past this point, the LNP keeps majority government',
#                    showarrow=True, arrowhead=0)

fig.update_layout(dict(plot_bgcolor='white'))
fig.update_xaxes(title_text='Possible LNP election results (number of seats)<br><i>Assuming all polling firms are equally accurate and seats with big minor party presence don\'t change hands</i>')
fig.update_yaxes(
    title_text=f'Number of outcomes (out of {len(shifts) * runs_per_shift} simulations)')
fig.update_layout(title=dict(text=f'LNP election outcomes with a polling s.d. of {sd}',
                             font=dict(color='black')))
fig.show()

print(f'LNP majority: {round(sum(totals_by_type[totals_by_type["seats"] >= 76]["outcomes"].values) / (len(shifts) * runs_per_shift) * 100, 2)}%')
print(f'ALP majority: {round(sum(totals_by_type[totals_by_type["seats"] <= 69]["outcomes"].values) / (len(shifts) * runs_per_shift) * 100, 2)}%')
