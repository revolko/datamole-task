from datetime import datetime
from typing import List


GITHUB_API_URL = "https://api.github.com/events"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def calculate_pr_avg_diff(events: dict, repo_id: int) -> float:
    """
    Calculate the average time between PRs for a given repository
    """

    pr_events = events['PullRequestEvent']
    repo_pr_events = list(filter(lambda e: e['repo']['id'] == repo_id, pr_events))

    total_diff = 0
    for i in range(len(repo_pr_events) - 1):
        first_e = datetime.strptime(repo_pr_events[i]['created_at'], DATETIME_FORMAT)
        second_e = datetime.strptime(repo_pr_events[i+1]['created_at'], DATETIME_FORMAT)
        datetime_diff = first_e - second_e
        total_diff += abs(datetime_diff.total_seconds())  # events are not strictly sorted by creation time

    return total_diff / (len(repo_pr_events) - 1)


def get_offset_events(events: dict, offset: int) -> dict:
    """
    Get events until offset
    """

    if offset == 0:
        return events

    current_time = datetime.now()
    offset_in_secs = offset * 60

    def filter_events(events_list: List) -> List:
        result = []
        for e in events_list:
            time_diff = current_time - datetime.strptime(e['created_at'], DATETIME_FORMAT)
            time_diff = time_diff.total_seconds()
            if time_diff <= offset_in_secs:
                result.append(e)

        return result

    for event_type in events:
        events[event_type] = filter_events(events[event_type])

    return events
