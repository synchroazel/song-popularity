import time
from datetime import datetime

from apiclient.discovery import build
from tqdm import tqdm

api_key = 'AIzaSyBrwNTSinLqhT7p-cOlVkzyUhkc5JAT9qM'
client = '168166509565-kl2ki885efpiff8h64v8c18npguq3ijj.apps.googleusercontent.com'
client_secret = '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'


class YoutubeHandler:
    '''
    TODO maybe not definitive
    '''

    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_by_keyword(self, query, max_results):
        next_page = ''
        all_titles = list()

        for _ in tqdm(range(max_results // 50)):
            request = self.youtube.search().list(q=query,
                                                 part='snippet',
                                                 type='music',
                                                 maxResults=50,
                                                 pageToken=next_page,
                                                 order='viewCount')
            res = request.execute()

            next_page = res['nextPageToken']
            all_titles.extend([vid['snippet']['title'] for vid in res['items']])

            time.sleep(1)

        print(f'Found {len(all_titles)} videos.')

        return res

    def search_by_id(self, id):
        request = self.youtube.videos().list(part=["snippet", "statistics"], id=id)
        res = request.execute()

        info = {'id': id,
                'title': res['items'][0]['snippet']['title'],
                'pub_date': res['items'][0]['snippet']['publishedAt'],
                'days_old': int((datetime.today() - datetime.strptime(res['items'][0]['snippet']['publishedAt'],
                                                                      '%Y-%m-%dT%H:%M:%SZ')).days),
                'views': int(res['items'][0]['statistics']['viewCount']),
                'likes': int(res['items'][0]['statistics']['likeCount']),
                'comments': int(res['items'][0]['statistics']['commentCount']),
                'channel': res['items'][0]['snippet']['channelTitle'],
                'tags': res['items'][0]['snippet']['tags']
                }

        info['popularity'] = info['views'] / info['days_old']

        return info


# %% TESTING

from pprint import pprint  # just for testing purposes, not in the final module

yt_handler = YoutubeHandler(api_key)

song_id1 = 'rLoGGMbF-YQ'  # Jovanotti - I love you baby
song_id2 = 'MA_5P3u0apQ'  # Mahmood & Blanco - Brividi

pprint(yt_handler.search_by_id(song_id1))
