import requests
import enum


GITHUB_API_URL = "https://api.github.com/events"


def get_events() -> dict:
    """
    Retrieve events from GitHub API.
    Filter out WatchEvent, PullRequestEvent, and IssuesEvent
    """

    resp = requests.get(url=GITHUB_API_URL)
    data = resp.json()

    events = {'WatchEvent': [], 'PullRequestEvent': [], 'IssuesEvent': []}

    for event in data:
        event_type = event['type']
        if event_type in events.keys():
            events[event_type].append(event)

    return events


def calculate_pr_avg_diff(events: dict, repo_id: int) -> float:
    """
    Calculate the average time between PRs for a given repository
    """

    pr_events = events['PullRequestEvent']
    repo_pr_events = filter(lambda e: e['repo']['id'] == repo_id, pr_events)

    total_diff = 0
    for i in range(len(repo_pr_events) - 1):
        pass

    return list(repo_pr_events)
