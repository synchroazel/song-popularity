import pandas as pd


def import_chart(filepath):
    """
    Quick function to import a .csv Spotify chart and make some modifications.
    In particular, colnames are parsed to be more readable and the track ids are extracted from their URLs.
    :param filepath: path to the the .csv chart to import
    :return: the chart as a pandas.DataFrame object
    """
    chart = pd.read_csv(filepath, header=1)
    chart.URL = chart.URL.str.replace('https://open.spotify.com/track/', '', regex=True)
    chart = chart.rename(columns={'URL': 'track_id',
                                  'Streams': 'streams',
                                  'Artist': 'artist',
                                  'Track Name': 'track_name'})

    chart = chart.drop('Position', axis=1)

    return chart
