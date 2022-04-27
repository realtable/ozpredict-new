import csv
import pickle
import pandas as pd
import plotly.express as px

with open('electorates.csv') as f:
    raw_electorates = [{k: v for k, v in row.items()}
                       for row in csv.DictReader(f, skipinitialspace=True)]

electorate_colors = {}
for i in raw_electorates:
    if i['party'].strip() in ['LIB', 'NAT', 'LNP']:
        # would go to ALP if flipped
        electorate_colors[i['elec_state'].strip()] = 'red'
    elif i['party'].strip() == 'ALP':
        # would go to LNP if flipped
        electorate_colors[i['elec_state'].strip()] = 'blue'
    else:
        electorate_colors[i['elec_state'].strip()] = 'grey'  # not relevant

with open('electorate_changes.p', 'rb') as f:
    raw_electorate_changes = pickle.load(f)

elec_label = 'Electorate (State)'
pct_label = 'Underestimation of LNP (0 is fairly accurate, 100 is as bad as 2019)'
electorate_changes = {
    elec_label: [],
    'Chance': [],
    pct_label: [],
}
for k, v in raw_electorate_changes.items():
    electorate_changes[elec_label].append(k[0])
    electorate_changes[pct_label].append(k[1])
    electorate_changes['Chance'].append(v)
df = pd.DataFrame(electorate_changes)

fig = px.scatter(df, x=elec_label, y='Chance', animation_frame=pct_label, hover_name=elec_label,
                 color=elec_label, color_discrete_map=electorate_colors)
fig.update_layout(dict(plot_bgcolor='white'))
fig.update_xaxes(showgrid=False,  # True, gridwidth=1, gridcolor='lightgrey',
                 zeroline=False,  # True, zerolinewidth=2, zerolinecolor='lightgrey',
                 showline=True, linewidth=1, linecolor='black', showticklabels=False,
                 title_text='Seats (hover to see names)')
fig.update_yaxes(showgrid=False,  # True, gridwidth=1, gridcolor='lightgrey',
                 zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                 # tickvals=[0, 50],
                 showline=True, linewidth=1, linecolor='black',
                 title_text='Chance (%age of simulations where seat flipped)')
fig.update_layout(title=dict(text='Chance of each seat flipping to party of colour shown',
                             font=dict(color='black')),
                  showlegend=False)
fig.show()
