from unittest import TestCase
from unittest.mock import patch
from datetime import datetime

from lib.metrics import calculate_pr_avg_diff, get_offset_events, get_public_repositories


class TestMetrics(TestCase):

    def setUp(self):
        super().setUp()

        self.events = {
            'PullRequestEvent': [
                {'id': '1', 'type': 'PullRequestEvent', 'repo': {'id': 1}, 'payload': {'action': 'opened'}, 'created_at': '2023-11-11T20:00:00Z'},
                {'id': '2', 'type': 'PullRequestEvent', 'repo': {'id': 1}, 'payload': {'action': 'opened'}, 'created_at': '2023-11-11T20:00:30Z'},
                {'id': '3', 'type': 'PullRequestEvent', 'repo': {'id': 1}, 'payload': {'action': 'opened'}, 'created_at': '2023-11-11T20:01:00Z'},
                {'id': '4', 'type': 'PullRequestEvent', 'repo': {'id': 2}, 'payload': {'action': 'opened'}, 'created_at': '2023-11-11T20:00:03Z'},
                {'id': '5', 'type': 'PullRequestEvent', 'repo': {'id': 2}, 'payload': {'action': 'opened'}, 'created_at': '2023-11-11T20:00:04Z'},
                {'id': '6', 'type': 'PullRequestEvent', 'repo': {'id': 1}, 'payload': {'action': 'closed'}, 'created_at': '2023-11-11T19:00:05Z'},
            ],
            'WatchEvent': [
                {'id': '7', 'type': 'WatchEvent', 'created_at': '2023-11-11T19:00:05Z'},
                {'id': '8', 'type': 'WatchEvent', 'created_at': '2023-11-11T20:00:05Z'},
            ],
            'IssuesEvent': [
                {'id': '9', 'type': 'IssuesEvent', 'created_at': '2023-11-11T19:00:05Z'},
                {'id': '10', 'type': 'IssuesEvent', 'created_at': '2023-11-11T19:00:05Z'},
                {'id': '11', 'type': 'IssuesEvent', 'created_at': '2023-11-11T20:00:05Z'},
                {'id': '12', 'type': 'IssuesEvent', 'created_at': '2023-11-11T20:11:05Z'},
            ],
            'PublicEvent': [
                {'id': '13', 'type': 'IssuesEvent', 'repo': {'name': 'publicRepo/one'}, 'created_at': '2023-11-11T20:1:05Z'},
                {'id': '14', 'type': 'IssuesEvent', 'repo': {'name': 'publicRepo/two'}, 'created_at': '2023-11-11T20:0:05Z'},
                {'id': '15', 'type': 'IssuesEvent', 'repo': {'name': 'publicRepo/three'}, 'created_at': '2023-11-11T19:0:05Z'},
            ],
        }

    def copy_events(self):
        return {event_type: events.copy() for event_type, events in self.events.items()}

    def test_calculate_pr_avg_diff(self):
        self.assertEqual(30.0, calculate_pr_avg_diff(self.copy_events(), 1))

    def test_calculate_pr_avg_diff_no_data(self):
        self.assertEqual(0.0, calculate_pr_avg_diff(self.copy_events(), 3))

    @patch('lib.metrics.datetime', wraps=datetime)
    def test_get_offset_events(self, fake_datetime):
        fake_datetime.now.return_value = datetime(2023, 11, 11, 20, 2)

        result = get_offset_events(self.copy_events(), 10)
        result_ids = {event_type: [e['id'] for e in events] for event_type, events in result.items()}

        expected_result_ids = {
                'PullRequestEvent': ['1', '2', '3', '4', '5'],
                'WatchEvent': ['8'],
                'IssuesEvent': ['11', '12'],
                'PublicEvent': ['13', '14'],
            }

        self.assertEqual(expected_result_ids, result_ids)

    def test_get_offset_events_no_offset(self):
        self.assertEqual(self.events, get_offset_events(self.copy_events(), offset=0))

    @patch('lib.metrics.datetime', wraps=datetime)
    def test_get_offset_events_all_with_offset(self, fake_datetime):
        fake_datetime.now.return_value = datetime(2023, 11, 11, 20, 2)

        self.assertEqual(self.events, get_offset_events(self.copy_events(), offset=62))

    def test_get_public_repositories(self):
        expected_result = ['publicRepo/one', 'publicRepo/two', 'publicRepo/three']
        self.assertEqual(expected_result, get_public_repositories(self.copy_events()))
