from flask import Flask, request

from lib import metrics, stream

app = Flask(__name__)
events = {'WatchEvent': [], 'PullRequestEvent': [], 'IssuesEvent': []}
stream.StreamThread(events).start()  # should make sure that deamon thread closes all I/O --> checkout atexit


@app.route("/pull_requests/<int:repo_id>", methods=['GET'])
def pull_requests(repo_id: int):
    """Calculate the average time between pull requests for a given repository."""

    global events
    events_copy = {e_type: es.copy() for e_type, es in events.items()}

    return {'avg_time': metrics.calculate_pr_avg_diff(events_copy, repo_id)}, 200


@app.route("/events", methods=['GET'])
def group_events():
    # TODO: take request.args.get('offset') into a consideration it will require to make a copy of events
    global events
    return {type: len(es) for type, es in events.items()}, 200
