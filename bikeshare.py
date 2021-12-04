# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:22:39 2021

@author: mooreb

Loads bikeshare data for a city, filters based on prompt inputs,
calculates statistics, and allows a view of the raw data.

"""

import time
import pandas as pd
import os
import datetime


AVAILABLE_CITIES = ['chicago', 'new york city', 'washington']
    


def get_city_file():
    """
    prompts the user for a city to load data for
    
    Asks the user for a city name to load data for. If the city is not available,
    a message is printed. City data is found by matching the (lowercase)
    city name to the file name (spaces are converted to underscores).
    Assumes the file is the same location as either the current working directory
    (where the prompt is executed from) or the file directory (where this file is stored).

    Returns
    -------
    city_file : STR
        Full path to file for data in city.

    """
    city_file = None
    cities_str = ', '.join([c.title() for c in AVAILABLE_CITIES])
    while city_file is None:
        user_city = input("Enter a city to explore ({}):  ".format(cities_str))
        if(user_city is None or user_city == ''):
            break #user did not enter anything -- exit loop
        
        try:
            city_num = int(user_city)
            if(city_num > 0 and city_num <= len(AVAILABLE_CITIES)):
                user_city = AVAILABLE_CITIES[city_num - 1]
            #not going to catch the value error for conversion to int
            #since we expect text (city name) but will handle specifically
            #the number associated with the city that was printed to the user
        finally:
            file_name = user_city.lower().replace(' ', '_') + ".csv"
            working_dir = os.getcwd()
            running_dir = os.path.dirname(os.path.realpath(__file__))
            fn = os.path.join(working_dir, file_name)
            if(not os.path.exists(fn)):
                fn = os.path.join(running_dir, file_name)
            if(os.path.exists(fn)):
                city_file = fn
                break
            else:
                print("\nSorry. No data for city '{}' at this time...".format(user_city.title()))
                print("\tCheck spelling or try another city.\n")
    return city_file


def get_month_filter(months=None):
    """
    prompts the USER for a month to filter data on

    Asks the user for a month, number or name, to filter selected csv file.
    If the months collection (parameter) is None, a generic list of all
    months (January through December) is generated.
    The user selected month (number,  name) is returned as a tuple.
    
    Parameters
    ----------
    months : LIST of INT, optional
        List of month options available for the user to select. The default is None.

    Returns
    -------
    month_filter : TUPLE of INT and STRING
        Month of year (1 = January) user selected and name of month
        NONE if user did not select one.

    """
    #months was not supplied -- build default list of month names
    #arbitrarily chose 2021 since just looping through months
    #to get month names
    min_month = 1
    max_month = 13 #12 months plus 1 for range
    if(months is not None):
        if(type(months[0]) != str):
            min_month = min(months)
            max_month = max(months) + 1
        else:
            min_month = datetime.datetime.strptime(months[0], '%B').month
            max_month = datetime.datetime.strptime(months[-1], '%B').month
    month_names = [datetime.datetime(2021, x, 1).strftime('%B') for x in range(min_month, max_month)]
    month_filter = None
    first_month = month_names[0]
    last_month = month_names[-1]
    user_month = input(f"[OPTIONAL] Enter a month to filter data ({first_month} to {last_month}):  ")
    if(user_month is not None and user_month != ''):
        try:
            #if the user input an integer
            #check if the user entered value is between 1 and 12
            #if the user entered value is not a valid month number
            #filter will remain None
            month_num = int(user_month)
            if(month_num > 0 and month_num <= 12):
                month_filter = (month_num + 1, month_names[month_num-1])
        except ValueError:
            #if the user input could not be cast to an integer
            #check to see if there is a match in the available months list
            #for the text the user entered
            user_month = user_month.title()
            if(month_names.count(user_month)):
                match = month_names.index(user_month)
                if(match > -1):
                    month_filter = (match + 1, user_month)
    return month_filter


def get_weekday_filter(weekdays=None):
    """
    prompts the USER for a weekday to filter data on
    
    Asks the user for a weekday, number or name, to filter selected csv file.
    If the weekdays collection (parameter) is None, a generic list of all
    weekdays (Monday through Sunday) is generated.
    The user selected weekday (number,  name) is returned as a tuple.

    Parameters
    ----------
    weekdays : LIST of STRING, optional
        List of weekday options available for the user to select. The default is None.

    Returns
    -------
    wkday_filter : TUPLE of INT and STRING
        Day of week (0 = Monday) user selected and name of the day
        NONE if user did not select one.

    """
    min_wkday = 1
    max_wkday = 7
    if(weekdays is not None):
        if(type(weekdays[0]) != str):
            #need to add 1 since 0 is not a valid month day number
            #this shift will move the end too
            min_wkday = min(weekdays) + 1
            max_wkday = max(weekdays) + 1
    else:
        #adding 1 to the max weekday number for use in range
        weekdays = [datetime.datetime(1990, 1, x).strftime('%A') for x in range(min_wkday, max_wkday + 1)]
    wkday_filter = None
    user_wkday = input("[OPTIONAL] Enter a day of the week to filter data:  ")
    if(user_wkday is not None and user_wkday != ''):
        try:
            #if the user input an integer
            #check if the user enterd value is between 0 and 6
            #if the user entered value is not a valid weekday number
            #filter will remain None
            wkday_num = int(user_wkday)
            if(wkday_num >= 0 and wkday_num < 7):
                wkday_filter = (wkday_num, weekdays[wkday_num-1])
        except ValueError:
            #if the user input could not be cast to an integer
            #check to see if there is a match in the available weekdays list
            #for the text the user entered
            user_wkday = user_wkday.title()
            if(weekdays.count(user_wkday) > 0):
                match = weekdays.index(user_wkday)
                if(match > -1):
                    wkday_filter = (match, user_wkday)
    return wkday_filter


def get_filters(ask_count=2):
    """
    prompts the user for parts needed to filter the data
    
    Prompts the user for the city name, month, and weekday.
    Asks for a confirmation whether filters and city are correct,
    asks again (up to ask_count times) if the user does not confirm.

    Parameters
    ----------
    ask_count : INT, optional
        The number of times to ask the user after the user does not confirm filters.
        The default is 2.

    Returns
    -------
    filters : TUPLE of STR, TUPLE, TUPLE
        User inputs to appropriately load and filter data from CSV.
        (csv_file, (month_num, month_name), (wkday_num, wkday_name))

    """
    filters = None
    while filters is None and ask_count > 0:
        city_file = get_city_file()
        if(city_file is not None):
            msg = f"We're going to look at {city_file}"
            df = None
            try:
                #going to pre-load the csv file
                #to get the available months for the dataset
                df = pd.read_csv(city_file)
                df['Start Time'] = pd.to_datetime(df['Start Time'])
                df['Month'] = df['Start Time'].dt.month
                df['DoW'] = df['Start Time'].dt.dayofweek
                months = sorted(df.Month.unique())
                month = get_month_filter(months)
                wkday = get_weekday_filter()
                if(month is not None and wkday is not None):
                    msg += f" for {wkday[1]} during {month[1]}"
                elif(month is not None):
                    msg += f" during {month[1]}"
                elif(wkday is not None):
                    msg += f" for {wkday[1]} during all months"
                else:
                    msg += " (no filters applied)"
                confirm = input(msg + '. Confirm?  ')
                if(confirm is not None and confirm != ''):
                    ask_count -= 1
                    if(confirm.lower().startswith('n')):
                        continue
                print('-=-'*15)
                filters = (city_file, month, wkday)
            except Exception as ex:
                print("Error getting filters for {}: {}".format(city_file, ex))
            finally:
                if(df is not None):
                    del(df)
    return filters


def load_data(datafile, month=None, dow=None):
    """
    loads data from csv file into a dataframe

    Reads the CSV file into a dataframe and filters based on user inputs

    Parameters
    ----------
    datafile : STR
        Path to the CSV file to load
    month : INT, optional
        The month to filter the loaded data on. The default is None.
    dow : INT, optional
        The day of the week to filter the loaded data on. The default is None.

    Returns
    -------
    df : PANDAS.DATAFRAME
        Pandas.DataFrame object containing data loaded from the CSV file and
        filtered based on parameters

    """
    df_csv = pd.read_csv(datafile)
    df_csv['Start Time'] = pd.to_datetime(df_csv['Start Time'])
    df_csv['End Time'] = pd.to_datetime(df_csv['End Time'])
    df_csv['Month'] = df_csv['Start Time'].dt.month
    df_csv['DoW'] = df_csv['Start Time'].dt.dayofweek
    df = df_csv.convert_dtypes()
    df.drop(df.columns[0], axis=1, inplace=True)
    if(month is None and dow is None):
        return df
    if(month is not None):
        df = df[df.Month == month[0]]
    if(dow is not None):
        df = df[df.DoW == dow[0]]
    return df
      

def calc_time_stats(dataframe):
    """
    calculates statistics about times of bikesharing
    
    Calculates time statistics:
    Most Common Month: mode of Month column (not calculated if filtered)
    Most Common Weekday: mode of DoW column (not calculated if filtered)
    Most Common Hour: mode of start time's hour field

    Parameters
    ----------
    dataframe : PANDAS.DATAFRAME
        Pandas DataFrame object containing data to calculate statistics for.

    Returns
    -------
    None.

    """
    if(dataframe is None):
        return
    print('Calculating the Most Frequent Times of Travel...\n')
    start_time = time.time()
    if(dataframe['Month'].unique().size > 1):
        most_month = dataframe['Month'].mode()
        if(most_month.size > 1):
            #tie for most frequent month
            month_names = []
            mm = most_month.array
            for i in range(mm.size):
                name = datetime.datetime(1990, mm[i], 1).strftime('%B')
                month_names.append(name)
            print('Most common Months:    {}'.format(', '.join(month_names)))
        else:
            most_month_name = datetime.datetime(1990, most_month, 1).strftime('%B')
            print('Most common Month:    {}'.format(most_month_name))
    if(dataframe['DoW'].unique().size > 1):
        most_wkday = dataframe['DoW'].mode()
        if(most_wkday.size > 1):
            #tie for most frequent weekday
            wkday_names = []
            mw = most_wkday.array
            for i in range(mw.size):
                name = datetime.datetime(1990, 1, mw[i] + 1).strftime('%A')
                wkday_names.append(name)
            print('Most common Weekdays:  {}'.format(', '.join(wkday_names)))
        else:
            most_wkday_name =datetime.datetime(1990, 1, most_wkday + 1).strftime('%A')
            print('Most common Weekday:  {}'.format(most_wkday_name))
    most_hour = dataframe['Start Time'].dt.hour.mode()
    if(most_hour.size > 1):
        hours = []
        mh = most_hour.array
        for i in range(mh.size):
            hour = mh[i]
            am_pm = 'AM'
            if(mh[i] >= 12):
                hour -= 12
                am_pm = 'PM'
                hours.append(f'{hour}{am_pm}')
        print('Most common Hours:     {}'.format(', '.join(hours)))
    else:
        hour = most_hour.array[0]
        am_pm = 'AM'
        if(hour >= 12):
            hour -= 12
            am_pm = 'PM'
        print('Most common Hour:     {}{}'.format(hour, am_pm))
    print(f'\nThis took {time.time() - start_time} seconds.')
    print('-=-'*15)
    
    
def calc_station_stats(dataframe):
    """
    calculates statistics about stations
    
    Calculates station statistics:
    Most Popular Start Station(s): most used station to start a trip
    Most Popular End Station(s): most used station to end a trip
    Most Popular Station Pair(s): most used start-end station pairings

    Parameters
    ----------
    dataframe : PANDAS.DATAFRAME
        Pandas DataFrame object containing data to calculate statistics for.

    Returns
    -------
    None.

    """
    if(dataframe is None):
        return
    print('Calculating the Most Popular Stations...\n')
    start_time = time.time()
    station1 = dataframe['Start Station'].mode()
    if(station1.size > 1):
        s1 = station1.array
        stations = []
        for i in range(s1.size):
            stations.append(s1[i])
        print('Most frequent Start Stations: {}'.format(', '.join(stations)))
    else:
        print('Most frequent Start Station: {}'.format(station1.iloc[0]))
    station2 = dataframe['End Station'].mode()
    if(station2.size > 1):
        s2 = station2.array
        stations = []
        for i in range(s2.size):
            stations.append(s2[i])
        print('Most Frequent End Stations: {}'.format(', '.join(stations)))
    else:
        print('Most Frequent End Station: {}'.format(station2.iloc[0]))
    station_pairs = pd.DataFrame(dataframe['Start Station'])
    station_pairs['End Station'] = dataframe['End Station']
    station_pairs.columns = ['Start', 'End']
    pairs = station_pairs.mode()
    spairs = []
    for i in range(len(pairs)):
        spairs.append('\t{} to {}'.format(pairs.iloc[i,0], pairs.iloc[i,1]))
    print('Most Frequent Trips:\n{}'.format('\n'.join(spairs)))
    print(f'\nThis took {time.time() - start_time} seconds.')
    print('-=-'*15)
    

def calc_trip_stats(dataframe):
    """
    calculates statistics about the trips taken
    
    Calculates trip statistics:
    Total trip duration: total time the bikes were used
    Mean trip duration: average time of a trip

    Parameters
    ----------
    dataframe : PANDAS.DATAFRAME
        Pandas DataFrame object containing data to calculate statistics for.

    Returns
    -------
    None.

    """
    if(dataframe is None):
        return
    print('Calculating Trip Duration...\n')
    start_time = time.time()
    total_time_span = dataframe['Trip Duration'].sum()
    mean_time_span = dataframe['Trip Duration'].mean()
    tt_d, tt_h, tt_m, tt_s = secs_to_full(total_time_span)
    mt_d, mt_h, mt_m, mt_s = secs_to_full(mean_time_span)
    time_str = '{} Days, {} Hours, {} Minutes and {} Seconds'.format(tt_d, tt_h, tt_m, tt_s)
    print('Total time of Trip Durations: {}'.format(time_str))
    if(mt_d > 0):
        time_str2 = '{} Days, {} Hours, {} Minutes and {} Seconds'.format(mt_d, mt_h, mt_m, mt_s)
    elif(mt_h > 0):
        time_str2 = '{} Hours, {} Minutes and {} Seconds'.format(mt_h, mt_m, mt_s)
    else:
        time_str2 = '{} Minutes and {} Seconds'.format(mt_m, mt_s)
    print('Mean time of Trip Durations: {}'.format(time_str2))
    print(f'\nThis took {time.time() - start_time} seconds.')
    print('-=-'*15)
    

def calc_user_stats(dataframe):
    """
    calculates statistics about the users
    
    Calculates user statistics:
    User Types: type name and count
    Gender: gender and count (if available)
    Birth Year: min, max, and mode (if availble)

    Parameters
    ----------
    dataframe : PANDAS.DATAFRAME
        Pandas DataFrame containing data to calculate statistics for.

    Returns
    -------
    None.

    """
    if(dataframe is None):
        return
    print('Calculating User Stats...\n')
    start_time = time.time()
    counts = dataframe['User Type'].value_counts()
    user_types = counts.index
    user_type_counts = []
    for i in range(user_types.size):
        ut = '\t{}: {}'.format(user_types[i], counts.iloc[i])
        user_type_counts.append(ut)
    print('User Types and Counts:\n{}'.format('\n'.join(user_type_counts)))
    if(list(dataframe.columns).count('Gender') > 0):
        counts2 = dataframe['Gender'].value_counts()
        genders = counts2.index
        gender_counts = []
        for i in range(genders.size):
            g = '\t{}: {}'.format(genders[i], counts2.iloc[i])
            gender_counts.append(g)
        print('Genders and Counts:\n{}'.format('\n'.join(gender_counts)))
    if(list(dataframe.columns).count('Birth Year') > 0):
        min_birth_year = dataframe['Birth Year'].min()
        max_birth_year = dataframe['Birth Year'].max()
        most_common_birth_year = None
        common_birth_year = dataframe['Birth Year'].mode()
        if(common_birth_year.size > 1):
            cby = common_birth_year.array
            commons = []
            for i in range(cby.size):
                commons.append(str(cby[i]))
            most_common_birth_year = ', '.join(commons)
        else:
            most_common_birth_year = common_birth_year.iloc[0]
        print('Min Birth Year: {}\nMax Birth Year: {}\nMost Common Birth Year: {}'
              .format(min_birth_year, max_birth_year, most_common_birth_year))
    print(f'\nThis took {time.time() - start_time} seconds.')
    print('-=-'*15)


def secs_to_full(seconds):
    days = 0
    hours = 0
    mins = 0
    secs = 0
    mins, secs = divmod(seconds, 60)
    if(mins > 60):
        hours, mins = divmod(mins, 60)
        if(hours > 24):
            days, hours = divmod(hours, 24)
    return (int(days), int(hours), int(mins), int(secs))


def view_raw(dataframe, start_index, count=5):
    """
    prints the raw data in the dataframe
    
    Prints to the console the raw data from the dataframe from the
    start_index to start_index + 5

    Parameters
    ----------
    dataframe : PANDAS.DATAFRAME
        Pandas DataFrame object containing data to print
    start_index : INT
        starting index of raw data
    count : INT, optional
        number of rows to print each time

    Returns
    -------
    INT
        the ending index for use in consecutive calls
        -1 if the dataframe is NONE

    """
    if(dataframe is None):
        return -1
    end_index = start_index + 5
    print(dataframe.iloc[start_index:end_index])
    return end_index


def prompt_T_F(msg):
    """
    prompts the user to given a message and returns True or False 

    Parameters
    ----------
    msg: STR
        Message to print to the user for input of yes/no question.
        
    Returns
    -------
    restart : BOOL
        user entered value: True for 'y' or empty, False for 'n'

    """
    tf = input(msg)
    if(tf is not None and tf != ''):
        if(tf.lower().startswith('n')):
            return False
    return True


def main():
    """
    The main execution of this script.
    """
    print("Hello! Let's explore some US bikeshare data!\n")
    
    while True:
        filters = get_filters()
        if(filters is None):
            break
        file, month, wkday = filters
        df = load_data(file, month, wkday)
        calc_time_stats(df)
        calc_station_stats(df)
        calc_trip_stats(df)
        calc_user_stats(df)
        view_data = input("\nWould you like to view this city's data?  ")
        if(view_data is None or view_data != ''):
            if(view_data.lower().startswith('n')):
                if(prompt_T_F('\nWould you like to restart?  ')):
                    continue
                else:
                    break
        pd.set_option('display.max_columns', df.columns.size)
        start_index = 0
        while start_index > -1:
            start_index = view_raw(df, start_index)
            stop = input('\nWould you like to view more?  ')
            if(stop is not None and stop != ''):
                if(stop.lower().startswith('n')):
                    break
        if(not prompt_T_F('\nWould you like to restart?  ')):
            break
    print('\n')
    print('*'*45)
    print('\nThank you for exploring bikeshare data!\n')
    print('*'*45)
    print('\n')
                    

if __name__ == '__main__':
    main()
        
        
    