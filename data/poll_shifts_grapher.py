import pickle
import pandas as pd
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

with open('poll_shifts.p', 'rb') as f:
    shifts = pickle.load(f)
with open('poll_current.p', 'rb') as f:
    polls = pickle.load(f)

plots = []

df = pd.DataFrame(polls)
for firm in list(dict.fromkeys(df['firm'])):
    x = df[df['firm'] == firm][df['until'] <= 200]['until'].values
    y = list(map(lambda x: x - 50, df[df['firm'] == firm][df['until'] <= 200]['LNP'].values))
    y_hat = lowess(y, x)
    plots.append(go.Scatter(x=x, y=y,
                            mode='markers', name=f'{firm} polls', opacity=0.4,
                            marker_color='black', marker_size=3)),
    plots.append(go.Scatter(x=y_hat[:, 0], y=y_hat[:, 1], name=f'{firm} avg',
                            line=dict(color='black')))
    final = (y_hat[:, 0][0], y_hat[:, 1][0])

    for year, year_shift in shifts[firm].items():
        plots.append(go.Scatter(x=[0, final[0]], y=[year_shift - 50, final[1]], name=f'{firm} movement if like {year}',
                                line=dict(color='red' if year_shift < 50 else 'blue')))

fig = go.Figure(plots)
fig.update_layout(dict(plot_bgcolor='white'))
fig.update_xaxes(showgrid=False, #True, gridwidth=1, gridcolor='lightgrey',
                 zeroline=True, zerolinewidth=2, zerolinecolor='lightgrey',
                 showline=True, linewidth=1, linecolor='black',
                 autorange='reversed', title_text='Days until election')
fig.update_yaxes(showgrid=False, #True, gridwidth=1, gridcolor='lightgrey',
                 zeroline=True, zerolinewidth=2, zerolinecolor='lightgrey',
                 showline=True, linewidth=1, linecolor='black',
                 title_text='LNP 2-party-preferred margin',)
fig.update_layout(title=dict(text="2022 polls with predicted movement (blue if LNP has 2PP >50)",
                             font=dict(color='black')))
fig.show()
