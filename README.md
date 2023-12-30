This repository has 3 functions:
- should fetch all the youtube subscriptions of a given user
  using the (partially completed) commmand line application
  dlp, and then persist all those subscriptions to a postgres
  database defined in the docker compose file.
- A python worker defined in worker should run that selects
  all the channels and videos for which the column `last_metrics_time`
  is older than the environment variable INTERVAL and should 
  retrieve the following metrics:
  - Channel:
    - view_count 
    - subscriber_count
    - video_count
    - short_video_count
    - total_video_duration
    - total_comment_count
    - total_likes
  - Video:
    - view_count
    - comment_count
    - like_count
    - comment_sentiment
    - retention_graph
    - duration
  and persist them in the postgres tables (defined in models) 
  youtube_video_metrics and youtube_channel_metrics.
- A grafana service (defined in docker compose and grafana dir)
  that should be able to query the postgres data source and display
  the youtube video and channel metrics effectively.

At the moment no logic has been defined to retrieve the metrics and the
worker is in essence incomplete.
The logic for fetching subscriptions and persisting them to the postgres
database should be functional.

Work is required to make this work.
  