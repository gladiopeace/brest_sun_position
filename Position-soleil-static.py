#!/usr/bin/env python
# coding: utf-8

# Position du soleil dans le ciel
# 
# "Static" code, to be automated with GA

import pandas as pd
import json

import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.ticker import MultipleLocator

# import pytz
from astral import sun
from astral import LocationInfo

# import locale
# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # Raise locale.Error: unsupported locale setting on Github actions

def daily_sun_position(day, obs):
    tim = pd.date_range(start='%s0000' % day, end='%i0000' % (int(day)+1), periods=288+1, tz='Europe/Paris')  # 5-mins
    altitude, azimuth = [], []
    for t in tim:
        altitude.append(sun.elevation(obs, t))# The number of degrees up from the horizon at which the sun can be seen
        azimuth.append(sun.azimuth(obs, t))   # The number of degrees clockwise from North at which the sun can be seen        
    df = pd.DataFrame(list(zip(tim, azimuth, altitude)), columns=['time', 'azimuth', 'altitude'])
    df['time'] = df['time'].dt.time
    return df

def get_xlim(this_df, vname='altitude', dx=5):
    return (
    pd.to_datetime("%s%0.2d%0.2d%0.2d"%(date,
    this_df.loc[this_df[vname]>=0].head(1)['time'].values[0].hour,
    this_df.loc[this_df[vname]>=0].head(1)['time'].values[0].minute,
    this_df.loc[this_df[vname]>=0].head(1)['time'].values[0].second))-pd.Timedelta(dx, unit='min')
    ,
    pd.to_datetime("%s%0.2d%0.2d%0.2d"%(date,
    this_df.loc[this_df[vname]>=0].tail(1)['time'].values[0].hour,
    this_df.loc[this_df[vname]>=0].tail(1)['time'].values[0].minute,
    this_df.loc[this_df[vname]>=0].tail(1)['time'].values[0].second))+pd.Timedelta(dx, unit='min')
    )


# Define date to work with
date = pd.to_datetime('now', utc='Europe/Paris').strftime("%Y%m%d")


# Define reference data
lon, lat = -4.5142170, 48.3814710  # Home ! Brest
l = LocationInfo('Brest', 'France', 'Europe/Paris', lat, lon)

# sunrise = sun.sunrise(l.observer).astimezone(pytz.timezone('Europe/Paris'))
# sunset = sun.sunset(l.observer).astimezone(pytz.timezone('Europe/Paris'))
# daylength = sunset-sunrise
# h = int(daylength.seconds/3600)
# m = int((daylength.seconds - h*3600)/60)
# s = int((daylength.seconds - h*3600 - m*60))
# print('sunrise: %s' % sunrise)
# print('sunset:  %s' % sunset)
# print('daylength: %i:%i:%i' % (h, m, s))

solstice_summer = daily_sun_position('%s0621' % date[0:4], l.observer)
solstice_winter = daily_sun_position('%s1221' % date[0:4], l.observer)


# Work with specific date
df = daily_sun_position(date, l.observer)

# Plot
# local_date = pd.to_datetime(date).strftime("%A %d %B %Y")
weekdays = {'Monday': 'Lundi',
           'Tuesday': 'Mardi',
           'Wednesday': 'Mercredi',
           'Thursday': 'Jeudi',
           'Friday': 'Vendredi',
           'Saturday': 'Samedi',
           'Sunday': 'Dimanche'}
months = {
    'January': 'Janvier',
    'February': 'Février',
    'March': 'Mars',
    'April': 'Avril',
    'May': 'Mai',
    'June': 'Juin',
    'July': 'Juillet',
    'August': 'Août',
    'September': 'Septembre',
    'October': 'Octobre',
    'November': 'Novembre',
    'December': 'Décembre'
}
local_date = "%s %s %s %s" % (
    weekdays[pd.to_datetime(date).strftime("%A")],
    pd.to_datetime(date).strftime("%d"),
    months[pd.to_datetime(date).strftime("%B")],
    pd.to_datetime(date).strftime("%Y"))

fig, ax = plt.subplots(ncols=2, sharey=True, figsize=(20, 7))

ax[0].plot(solstice_winter['azimuth'], solstice_winter['altitude'], 'b', label="Solstice d'hiver", linewidth=2)
ax[0].plot(df['azimuth'], df['altitude'], 'k', label=local_date, linewidth=3)
ax[0].plot(solstice_summer['azimuth'], solstice_summer['altitude'], 'r', label="Solstice d'été", linewidth=2)
ax[0].xaxis.set_minor_locator(MultipleLocator(10))
ax[0].xaxis.set_major_locator(MultipleLocator(20))
ax[0].grid(visible=True, which='minor', color='lightgray', linestyle='--')
ax[0].grid(visible=True, which='major', color='gray', linestyle='-')
ax[0].set_xlabel('Azimuth [deg]')
ax[0].set_ylabel('Altitude [deg]')
ax[0].set_xlim(solstice_summer.loc[solstice_summer['altitude']>=0].head(1)['azimuth'].values[0]-5, 
               solstice_summer.loc[solstice_summer['altitude']>=0].tail(1)['azimuth'].values[0]+5)
ax[0].vlines([90, 180, 270], 0, 90, color='black', linewidth=1)
ax[0].text( 90-1, 90, 'E', horizontalalignment='right', verticalalignment='top', color='r')
ax[0].text(180-1, 90, 'S', horizontalalignment='right', verticalalignment='top', color='r')
ax[0].text(270-1, 90, 'W', horizontalalignment='right', verticalalignment='top', color='r')

ax[1].plot(pd.to_datetime(date + " " + solstice_winter['time'].astype(str)) , solstice_winter['altitude'], 'b', label="Solstice d'hiver", linewidth=2)
ax[1].plot(pd.to_datetime(date + " " + df['time'].astype(str)), df['altitude'], 'k', label=local_date, linewidth=3)
ax[1].plot(pd.to_datetime(date + " " + solstice_summer['time'].astype(str)) , solstice_summer['altitude'], 'r', label="Solstice d'été", linewidth=2)
ax[1].xaxis.axis_date(tz='Europe/Paris')
ax[1].xaxis.set_major_locator(dates.HourLocator())
ax[1].xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
plt.setp(plt.gca().xaxis.get_majorticklabels(), 'rotation', 45)
ax[1].grid()
ax[1].set_ylim([0,90])
ax[1].set_xlabel('Temps')
ax[1].set_xlim(get_xlim(solstice_summer, dx=15));
ax[1].legend()

fig.suptitle("Position et course du soleil\n%s, %s/%s" % (local_date, l.name, l.region), fontsize=16);

fig.tight_layout()
fig.savefig('position_soleil.png', dpi=200, transparent=False)

# Save some files:
with open('last_update.json', 'w') as outfile:
    json.dump({"schemaVersion": 1,
               "label": "Dernière mise à jour",
               "message": local_date,
               "color": "green"}, outfile)

t = pd.to_datetime('now', utc='Europe/Paris')
with open('current_altitude.json', 'w') as outfile:
    json.dump({"schemaVersion": 1,
               "label": "Altitude",
               "message": "%0.3f" % sun.elevation(l.observer, t),
               "color": "green"}, outfile)

with open('current_azimuth.json', 'w') as outfile:
    json.dump({"schemaVersion": 1,
               "label": "Azimuth",
               "message": "%0.3f" % sun.azimuth(l.observer, t),
               "color": "green"}, outfile)