import pandas as pd


def import_chart(filepath):
    """
    Imports a .csv chart from its path.

    :param filepath: path to the the .csv file to import
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
