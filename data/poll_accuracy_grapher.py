import pickle
import pandas as pd
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.interpolate import interp1d

with open('poll_accuracy.p', 'rb') as f:
    trends = pickle.load(f)

plots = []
current = 2022
colors = {
    2022: '#dd0000',
    2019: '#004400',
    2016: '#009900',
    2013: '#99dd99'
}
finals = {
    2019: {},
    2016: {},
    2013: {}
}
shifts = {}

for year, year_data in sorted(trends.items()):
    for firm, firm_data in year_data.items():
        df = pd.DataFrame(firm_data)
        x = df['until'].values
        y = df['diff'].values
        y_hat = lowess(y, x)

        if year != current:
            # do graph stuff (in which case y gives inaccuracy)
            plots.append(go.Scatter(x=y_hat[:, 0], y=y_hat[:, 1], name=f'{firm} avg in {year}',
                                    line=dict(color=colors[year])))
            if y_hat[:, 0][0] <= 10:
                finals[year][firm] = y_hat[:, 1][0]

        else:
            # do prediction stuff (in which case y gives margin over 50)
            x_new = [x.min(), 0]
            interp = interp1d(
                y_hat[:, 0], y_hat[:, 1], bounds_error=False, kind='linear', fill_value='extrapolate')
            y_new = interp(x_new)
            for f_year in [2013, 2016, 2019]:
                if firm in finals[f_year]:
                    # print(f'{firm} like {f_year} goes from {round(50 + y_new[-1], 1)} to {round(50 + y_new[-1] - finals[f_year][firm], 1)}')
                    if firm not in shifts:
                        shifts[firm] = {}
                        shifts[firm]['simple'] = round(50 + y_new[-1], 1)
                    shifts[firm][f_year] = round(
                        50 + y_new[-1] - finals[f_year][firm], 1)

with open('poll_shifts.p', 'wb+') as f:
    pickle.dump(shifts, f)

fig = go.Figure(plots)
fig.update_layout(dict(plot_bgcolor='white'))
fig.update_xaxes(showgrid=False, #True, gridwidth=1, gridcolor='lightgrey',
                 zeroline=True, zerolinewidth=2, zerolinecolor='lightgrey',
                 showline=True, linewidth=1, linecolor='black',
                 autorange='reversed', title_text='Days until election')
fig.update_yaxes(showgrid=False, #True, gridwidth=1, gridcolor='lightgrey',
                 zeroline=True, zerolinewidth=2, zerolinecolor='lightgrey',
                 showline=True, linewidth=1, linecolor='black',
                 title_text='Polls relative to election result')
fig.update_layout(title=dict(text='LNP 2-party-preferred polls for 200 days before election',
                             font=dict(color='black')))
fig.show()
