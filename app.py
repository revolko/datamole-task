from flask import Flask, request

from lib import metrics, stream

app = Flask(__name__)
events = {'WatchEvent': [], 'PullRequestEvent': [], 'IssuesEvent': []}
stream.StreamThread(events).start()


@app.route("/pull_requests/<int:repo_id>", methods=['GET'])
def pull_requests(repo_id: int):
    """Calculate the average time between pull requests for a given repository."""

    global events
    events_copy = {e_type: es.copy() for e_type, es in events.items()}

    return {'avg_time': metrics.calculate_pr_avg_diff(events_copy, repo_id)}, 200


@app.route("/events", methods=['GET'])
def group_events():
    global events
    events_copy = {e_type: es.copy() for e_type, es in events.items()}

    offset = int(request.args.get('offset', '0'))
    filtered_events = metrics.get_offset_events(events_copy, offset)
    return {event_type: len(event_list) for event_type, event_list in filtered_events.items()}, 200
