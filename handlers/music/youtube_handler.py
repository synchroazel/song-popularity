import time
from datetime import datetime

from apiclient.discovery import build
from tqdm import tqdm

import secrets

api_key = secrets.yt_api_key
client = secrets.yt_client
client_secret = secrets.yt_client_secret


class YoutubeHandler:
    """
    Includes a set of methods to interact with YouTube APIs.
    """

    def __init__(self, api_key=api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_song(self, song_name, artist_name, quiet=True):
        """
        Returns video id from a song name and its artist's name.
        """

        res = self.search_by_keyword(f'{song_name} {artist_name}', 50, quiet=quiet)

        best_result = [item for item in res['items'] if (song_name.lower() in item['snippet']['title'].lower() and
                                                         artist_name.lower() in item['snippet']['title'].lower())][0]

        video_id = best_result["id"]["videoId"]

        return self.search_by_id(video_id)

    def search_by_keyword(self, query, max_results, quiet=False):
        """
        Performs a video search by keyword, and returns the response as dict.
        """

        next_page = ''
        all_titles = list()
        max_results = 50 if max_results > 50 else max_results

        for _ in tqdm(range(max_results // 50), disable=quiet):
            request = self.youtube.search().list(q=query,
                                                 part='snippet',
                                                 type='music',
                                                 maxResults=50,
                                                 pageToken=next_page,
                                                 order='viewCount')
            r = request.execute()

            all_titles.extend([vid['snippet']['title'] for vid in r['items']])

            try:
                next_page = r['nextPageToken']
            except:
                break

            time.sleep(5)

        return r

    def search_by_id(self, id):
        """
        Returns information on a video as a dict from its id.
        """

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
                'channel': res['items'][0]['snippet']['channelTitle']
                }

        info['popularity'] = info['views'] / info['days_old']

        return info
