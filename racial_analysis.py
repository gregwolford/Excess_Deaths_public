
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 08:24:44 2020

Analysis of COVID Racial Data

@author: gregn
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import wrappers.thinking_statistically as ts
import plotly.figure_factory as ff
from wrappers.plots import sns_plot, sns_bee_box
from wrappers.load import get_totals, get_from_url, get_wbh, fold_totals
from wrappers.load import get_total_incidents, breakout_incidents, load_from_url
from wrappers.load import get_state_by_eth, breakout_ethnicities, get_incidents

"""
Following turns off the 'SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.' warning
"""
pd.options.mode.chained_assignment = None  # default='warn'


data_url = r'https://docs.google.com/spreadsheets/d/e/2PACX-1vR_xmYt4ACPDZCDJcY12kCiMiH0ODyx3E1ZvgOHB8ae1tRcjXbs_yWBOA4j4uoCEADVfC1PS2jYO68B/pub?gid=43720681&single=true&output=csv'

"""
Population Data from https://www.census.gov/quickfacts/fact/table/US/PST045219
"""

"""
-----------------------------------------------
Constants and static URLs
-----------------------------------------------
"""

data_url = r'https://docs.google.com/spreadsheets/d/e/2PACX-1vR_xmYt4ACPDZCDJcY12kCiMiH0ODyx3E1ZvgOHB8ae1tRcjXbs_yWBOA4j4uoCEADVfC1PS2jYO68B/pub?gid=43720681&single=true&output=csv'
pop_url = r'data/state_pops.csv'
eth_url = r'data/us_eth_by_state.csv'

ethnic_case_cols = ['State','Cases_White', 'Cases_Black', 'Cases_LatinX', 'Cases_Asian', 'Cases_AIAN', 'Cases_Multiracial', 
                    'Cases_Other', 'Cases_Unknown']
case_rename = {'Cases_White':'White', 'Cases_Black':'Black', 'Cases_LatinX':'LatinX', 'Cases_Asian':'Asian', 
               'Cases_AIAN':'AIAN', 'Cases_Multiracial':'Multiracial', 'Cases_Other':'Other', 'Cases_Unknown':'Unknown'}

ethnic_deaths_cols = ['State','Deaths_White', 'Deaths_Black', 'Deaths_LatinX', 'Deaths_Asian', 'Deaths_AIAN', 'Deaths_Multiracial', 
                    'Deaths_Other', 'Deaths_Unknown']

deaths_rename = {'Deaths_White':'White', 'Deaths_Black':'Black', 'Deaths_LatinX':'LatinX', 'Deaths_Asian':'Asian', 
               'Deaths_AIAN':'AIAN', 'Deaths_Multiracial':'Multiracial', 'Deaths_Other':'Other', 'Deaths_Unknown':'Unknown'}



us_pop = 328239523
pop_perc={'Ethnicity':['White', 'Black', 'LatinX', 'Asian', 'AIAN', 'Multiracial', 'Other'], 
          'Percent':[0.601, 0.134, 0.185, 0.059, 0.013, 0.028, 0.02]}
pop = pd.DataFrame.from_dict(pop_perc)
pop['Population'] = pop['Percent']*us_pop

"""
----------------------------------------------------
Load Case Data
----------------------------------------------------
"""

data = load_from_url(data_url, index = 'Date', parse_dates = 'Date')

state_pop = get_from_url(pop_url)
state_eth = get_from_url(eth_url, fix_black=True)
cases = get_incidents(data, ethnic_case_cols, case_rename, state_pop, fix_white=True)
deaths = get_incidents(data, ethnic_deaths_cols, deaths_rename, state_pop)

state_by_eth = get_state_by_eth(state_eth)
white, black, hispanic, combined = breakout_ethnicities(state_by_eth, state_pop)

total_cases = get_total_incidents(cases)
total_deaths = get_total_incidents(deaths)
cases_wbh = get_wbh(cases)
white_cases, black_cases, hispanic_cases, combined_cases = breakout_incidents(cases_wbh, state_by_eth)

deaths_wbh = get_wbh(deaths)
white_deaths, black_deaths, hispanic_deaths, combined_deaths = breakout_incidents(deaths_wbh, state_by_eth)

case_totals = get_totals(cases.iloc[:, :-6])
case_totals['Percent Cases'] = case_totals['Total']/cases['Total Cases'].sum()

death_totals = get_totals(deaths.iloc[:, :-6])
death_totals['Percent Deaths'] = death_totals['Total']/deaths['Total Cases'].sum()

# Fold totals data for side by side comparison of population/cases/deaths
f_all = fold_totals(pop, case_totals, death_totals)

# View combined bar chart
sns_plot(f_all, 'Ethnicity', 'Percent', 'Percent by Ethnicity/Race', 'catplot', hue='Legend', kind='bar')

#fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, sharey=False)
ax1 = sns.swarmplot(x='Ethnicity', y='Ethnic Distribution', data=combined, order=['White', 'Black', 'Hispanic'])
sns.boxplot(x='Ethnicity', y='Ethnic Distribution', data = combined, showcaps=False, boxprops={'facecolor':'None'}, showfliers=False, ax=ax1, order=['White', 'Black', 'Hispanic'])
plt.show()
plt.clf()

ax2 = sns.swarmplot(x='Ethnicity', y='Ethnic Distribution', data=combined_cases)
sns.boxplot(x='Ethnicity', y='Ethnic Distribution', data = combined_cases, showcaps=False, boxprops={'facecolor':'None'}, showfliers=False, ax=ax2)
plt.show()
plt.clf()

ax3 = sns.swarmplot(x='Ethnicity', y='Ethnic Distribution', data=combined_deaths)
sns.boxplot(x='Ethnicity', y='Ethnic Distribution', data = combined_deaths, showcaps=False, boxprops={'facecolor':'None'}, showfliers=False, ax=ax3)
plt.show()
plt.clf()





"""
ax=sns_bee_box(state_by_eth, 'Ethnicity', 'Percent Population', 'Percent by Ethnicity/Race')
combined_cases['Scaled Percent'] = combined_cases['Percent Population']*1000
ax1=sns_bee_box(combined_cases, 'Ethnicity', 'Percent Population', 'Cases by Ethnicity/Race')
combined_deaths['Scaled Percent'] = combined_deaths['Percent Population']*1000
ax2=sns_bee_box(combined_deaths, 'Ethnicity', 'Percent Population', 'Cases by Ethnicity/Race')

plt.show()
plt.clf()
"""




