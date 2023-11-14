from datetime import datetime
from typing import List


GITHUB_API_URL = "https://api.github.com/events"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def calculate_pr_avg_diff(events: dict, repo_id: int) -> float:
    """
    Calculate the average time between PRs for a given repository
    """

    pr_events = events['PullRequestEvent']
    pr_events_len = len(pr_events)  # instead of copying the whole list, remember the last item
    repo_pr_events = [pr_events[i] for i in range(pr_events_len)
                      if pr_events[i]['repo']['id'] == repo_id
                      and pr_events[i]['payload']['action'] == 'opened']

    if len(repo_pr_events) <= 1:
        return 0.0

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
    # decrese memory allocation by remembering the last item for each type
    events_len = {event_type: len(events_list) for event_type, events_list in events.items()}

    def filter_events(events_list: List, list_len: int) -> List:
        result = []
        for i in range(list_len):
            time_diff = current_time - datetime.strptime(events_list[i]['created_at'], DATETIME_FORMAT)
            time_diff = time_diff.total_seconds()
            if time_diff <= offset_in_secs:
                result.append(events_list[i])

        return result

    for event_type in events:
        events[event_type] = filter_events(events[event_type], events_len[event_type])

    return events


def get_public_repositories(events: dict) -> List:
    """
    Get repositories which were made public
    """

    public_events = events['PublicEvent']
    events_len = len(public_events)

    return [public_events[i]['repo']['name'] for i in range(events_len)]
