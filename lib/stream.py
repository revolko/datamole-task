import threading
import time
import requests
import os

from dotenv import load_dotenv
from typing import List

load_dotenv()  # Load .env variables to environment variables


class ConnectionError(Exception):

    def __init__(self, response: requests.Response):
        self.status_code = response.status_code
        self.error = response.text

    def __str__(self):
        return f'Request to GITHUB API failed with status code = "{self.status_code}".\n'\
                f'Error text: "{self.error}'


class StreamThread(threading.Thread):

    PAGE_SIZE = 100
    EVENTS_API_URL = f'https://api.github.com/events?page_size={PAGE_SIZE}'

    def __init__(self, events: dict):
        threading.Thread.__init__(self, daemon=True)
        self.events = events
        self.found_ids = set()
        self.session = requests.Session()

        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            self.session.headers.update({'Authorization': f'Bearer {github_token}'})

        self.session.headers.update({'Accept': 'application/vnd.github+json'})
        self.last_etag = ''
        self.poll_rate_limit = 60
        self.timeout = 1

    @staticmethod
    def get_last_etag(res_headers):
        etag = res_headers.get('ETag', '')
        return etag.lstrip('/W')

    def handle_connection_error(self, resposne: requests.Response):
        if resposne.status_code == 403:
            # reached the limit of API connections
            self.timeout *= 2
            time.sleep(self.timeout)
        else:
            self.session.close()
            raise ConnectionError(resposne)

    def get_events(self, url: str) -> List:
        res = self.session.get(url, headers={'if-none-match': self.last_etag})
        self.last_etag = self.get_last_etag(res.headers)
        self.poll_rate_limit = int(res.headers.get('X-RateLimit-Limit', '60'))

        if res.status_code == 304:
            # based on the ETag there are no new events
            return []

        if res.status_code >= 400:
            # API error
            self.handle_connection_error(res)
            return []

        self.timeout = 1  # no error --> reset timeout
        return res.json()

    def filter_events(self, data: List):
        for event in data:
            event_id = event['id']
            if event_id in self.found_ids:
                continue

            self.found_ids.add(event_id)
            event_type = event['type']
            if event_type in self.events.keys():
                self.events[event_type].append(event)

    def poll_wait(self):
        """
        X-RateLimit-Limit defines the maximum number of requests that can be executed
        againts the GitHub API in an hour. Polling 3 pages (due to page_size == 100) requires
        3 requests; thus the limit is X-RateLimit-Limit / 3
        """

        time.sleep(3600 / (self.poll_rate_limit / 3))

    def run(self):
        while True:
            data = self.get_events(self.EVENTS_API_URL)
            self.filter_events(data)
            for i in range(2, 4):
                data = self.get_events(f'{self.EVENTS_API_URL}&page={i}')
                self.filter_events(data)

            self.poll_wait()
