# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 19:04:01 2020

@author: gregn
"""
import pandas as pd
import numpy as np
import os
from wrappers.configuration import Configuration

"""
Following turns off the 'SettingWithCopyWarning:
A value is trying to be set on a copy of a slice from a DataFrame.' warning
"""
#pd.options.mode.chained_assignment = None  # default='warn'

# Get API key for Chart Studio Account
cf = Configuration(r'wrappers/config.txt')
username = cf.username
api_key = cf.api_key

drop_cols = ['Type', 'Outcome', 'Suppress', 'Note']
excess = pd.read_csv('data\Excess_Deaths_Associated_with_COVID-19.csv')
excess.drop(columns = drop_cols)
excess['Week Ending Date'] = pd.to_datetime(excess['Week Ending Date'])
excess.set_index('Week Ending Date')
excess['Lower Bound Threshold'] = excess['Average Expected Count'] - (excess['Upper Bound Threshold'] - excess['Average Expected Count'])
excess['Observed Exceed Expected'] = excess['Observed Number'] - excess['Average Expected Count']
excess['Observed Exceed Upper'] = excess['Observed Number'] - excess['Upper Bound Threshold']
excess['Observed Exceed Lower'] = excess['Observed Number'] - excess['Lower Bound Threshold']
excess_all = excess[
                    (excess['State'] == 'United States') &
                    (excess['Outcome'] == 'All causes') &
                    (excess['Type'] != 'Unweighted')]

excess_excludes_covid = excess[(excess['State'] == 'United States') &
                               (excess['Outcome'] == 'All causes, excluding COVID-19') &
                                (excess['Type'] != 'Unweighted')]

excess_all.drop(excess_all.tail(3).index, inplace=True)
excess_all.tail()

excess_excludes_covid.drop(excess_excludes_covid.tail(3).index, inplace=True)
excess_excludes_covid.tail()

excess_all.set_index('Week Ending Date', inplace=True)
excess_excludes_covid.set_index('Week Ending Date', inplace=True)

import plotly.express as px
import plotly.graph_objects as go
import chart_studio
import chart_studio.plotly as py

chart_studio.tools.set_credentials_file(username = username, api_key = api_key)
chart_studio.tools.set_config_file(world_readable=True, sharing='public')
actual = np.array(excess_all['Observed Number'])
upper = np.array(excess_all['Upper Bound Threshold'])
dates = excess_all.index
lower = np.array(excess_all['Lower Bound Threshold'])

"""
trace1 = go.Scatter(
        name='Actual',
        x=dates,
        y=actual,
        line=dict(color='rgb(31, 119, 180)'),
        mode='lines'
    )

trace2 =  go.Scatter(
        name='Upper Bound',
        x=dates,
        y=upper, # upper, then lower reversed
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
    )

trace3 = go.Scatter(
        name='Lower Bound',
        x=dates,
        y=lower,
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    )

data = [trace1, trace2, trace3]
py.plot(data, filename = 'excess_deaths', auto_open = True)
"""


fig = go.Figure([
   go.Scatter(
        name='Actual',
        x=dates,
        y=actual,
        line=dict(color='rgb(31, 119, 180)'),
        mode='lines'
    ),
    go.Scatter(
        name='Upper Bound',
        x=dates,
        y=upper, # upper, then lower reversed
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
    ),
    go.Scatter(
        name='Lower Bound',
        x=dates,
        y=lower,
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    )
])
fig.update_layout(
    yaxis_title='Deaths',
    xaxis_title='Date',
    title='Expected Deaths by week',
    hovermode="x"
   
)

fig['layout']['title'] = 'Actual deaths vs. expected deaths'
py.iplot(fig, filename="actual-vs-expected", auto_open = True)

#fig.show()


from wrappers.thinking_statistically import permutation_test, shifted_means_test, pearson_r

covid_start = '2020-02-29'
covid_deaths = np.array(excess_all[covid_start:]['Observed Number'])
pre_covid_deaths = np.array(excess_all.loc[:covid_start]['Observed Number'])
covid_excess = np.array(excess_all[covid_start:]['Observed Exceed Expected'])

permutation_test(covid_deaths,
                    pre_covid_deaths,
                    '\nPermutation test of Covid deaths to observed deaths\n',
                    'P-Value of a difference between {} deaths and {} deaths = {:.4f}',
                    'Covid',
                    'Observed')

shifted_means_test(np.array(excess['Observed Number']), covid_deaths, pre_covid_deaths,
                            'Covid', 'Observed', sample_size=10000)

print('Excess deaths above average: {:,.0f}'.format(covid_excess.sum()))
print('Excess deaths above upper bound: {:,.0f}'.format(excess_all[covid_start:]['Observed Exceed Upper'].sum()))
print('Excess deaths above lower bound: {:,.0f}'.format(excess_all[covid_start:]['Observed Exceed Lower'].sum()))

scaled_covid_deaths = covid_excess * 10
col_list = ['submission_date', 'tot_cases', 'new_case']
covid_cases = pd.read_csv('data/United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv', 
                          parse_dates = True, 
                          index_col = 'submission_date',
                          usecols = col_list)
covid_cases = covid_cases.groupby(level = 'submission_date').sum()
covid_cases = covid_cases.resample('W').sum()
covid_cases = covid_cases[(covid_cases.index > '2020-02-29') & (covid_cases.index <= '2020-08-09')]
scaled_covid_deaths.shape

fig = go.Figure()
fig.add_trace(go.Scatter(x = covid_cases.index,
                         y = covid_cases['new_case'],
                         mode = 'lines',
                         name = 'Covid cases'))
fig.add_trace(go.Scatter(x = covid_cases.index,
                         y = scaled_covid_deaths, 
                        mode = 'lines',
                        name = 'Covid deaths (scaled)'))

fig['layout']['title'] = 'Covid cases compared to Covid deaths (scaled)'
py.iplot(fig, filename="cases-to-deaths", auto_open = True)

#fig.show()


