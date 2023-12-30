import logging

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import json
from datetime import datetime
from datetime import datetime
import re

def parse_date_string(date_string):
    try:
        if re.match(r'\d+ \w+ ago', date_string):  # Example pattern for relative dates
            # Custom logic to handle relative dates like '1 year ago'
            # This will depend on your specific needs
            return calculate_relative_date(date_string)
        else:
            # Handle absolute date formats
            try:
                return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')  # ISO 8601 format
            except ValueError:
                return datetime.strptime(date_string, '%d %b %Y')  # Another absolute format
    except Exception as e:
        logging.exception(e)

def calculate_relative_date(relative_date_string):
    # Implement the logic to calculate the actual date from the relative date string
    # This is just a placeholder function
    return datetime.now()  # Placeholder, replace with actual logic

# Example usage

Base = declarative_base()




class Channel(Base):
    __tablename__ = 'youtube_channel'

    id = Column(String)
    channel_id = Column(String, primary_key=True)

    kind = Column(String)
    etag = Column(String)
    title = Column(String)
    description = Column(String)
    custom_url = Column(String)
    published_at = Column(String)
    thumbnail_default_url = Column(String)
    thumbnail_medium_url = Column(String)
    thumbnail_high_url = Column(String)
    thumbnail_standard_url = Column(String)
    thumbnail_maxres_url = Column(String)
    country = Column(String)
    view_count = Column(Integer)
    subscriber_count = Column(Integer)
    hidden_subscriber_count = Column(Boolean)
    video_count = Column(Integer)
    privacy_status = Column(String)
    is_linked = Column(Boolean)
    long_uploads_status = Column(String)
    made_for_kids = Column(Boolean)
    banner_external_url = Column(String)
    related_playlist_likes = Column(String)
    related_playlist_uploads = Column(String)
    topic_ids = Column(String)
    topic_categories = Column(String)
    last_metrics_time = Column(DateTime)

    video_metrics = relationship("VideoMetric", back_populates="channel")
    metrics = relationship("ChannelMetric", back_populates="metrics")
    videos = relationship("Video")


    def __init__(self, json_data):
        self.id = json_data['id']
        self.kind = json_data['kind']
        self.etag = json_data['etag']
        snippet = json_data['snippet']
        self.title = snippet['title']
        self.description = snippet['description']
        self.custom_url = snippet.get('customUrl', None)
        self.published_at = snippet['publishedAt']
        thumbnails = snippet['thumbnails']
        self.thumbnail_default_url = thumbnails['default']['url'] if thumbnails.get('default') else None
        self.thumbnail_medium_url = thumbnails['medium']['url'] if thumbnails.get('medium') else None
        self.thumbnail_high_url = thumbnails['high']['url'] if thumbnails.get('high') else None
        self.country = snippet.get('country', None)
        statistics = json_data['statistics']
        self.view_count = int(statistics['viewCount'])
        self.subscriber_count = int(statistics['subscriberCount'])
        self.hidden_subscriber_count = statistics['hiddenSubscriberCount']
        self.video_count = int(statistics['videoCount'])
        status = json_data['status']
        self.privacy_status = status['privacyStatus']
        self.is_linked = status['isLinked']
        self.long_uploads_status = status['longUploadsStatus']
        self.made_for_kids = status['madeForKids']
        branding = json_data['brandingSettings']
        self.banner_external_url = branding['image']['bannerExternalUrl']
        content_details = json_data['contentDetails']
        related_playlists = content_details['relatedPlaylists']
        self.related_playlist_likes = related_playlists['likes']
        self.related_playlist_uploads = related_playlists['uploads']
        topic_details = json_data['topicDetails']
        self.topic_ids = ', '.join(topic_details['topicIds'])
        self.topic_categories = ', '.join(topic_details['topicCategories'])


class Subscription(Channel):
    pass

class ChannelMetric(Base):
    def __init__(self):
        __tablename__ = 'youtube_channel_metrics'

        # Primary Key
        channel_metric_id = Column(String, primary_key=True)
        created_at = Column(DateTime)
        channel_id = Column(String, ForeignKey('youtube_channel.channel_id'))

        view_count = Column(Integer)
        subscriber_count = Column(Integer)
        video_count = Column(Integer)
        short_video_count = Column(Integer)
        total_video_duration = Column(Integer)
        total_comment_count = Column(Integer)
        total_likes = Column(Integer)

        channel = relationship("Channel", back_populates="metrics")



class Video(Base):
    __tablename__ = 'youtube_video'

    # Primary Key
    video_id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey('youtube_channel.channel_id'))

    # Attributes
    title = Column(String)
    description = Column(String)
    published_time = Column(DateTime)
    persisted_time = Column(DateTime)
    last_metrics_time = Column(DateTime)
    length_text = Column(String)
    rich_thumbnail_url = Column(String)
    view_count = Column(Integer)   


    channel = relationship("Channel")
    metrics = relationship("VideoMetric", back_populates="video")


    @staticmethod
    def extract(json_data):
        # Extract thumbnail URLs correctly
        try:
            return {
                'video_id': json_data.get('videoId', ''),
                'title': json_data.get('title', {}).get('runs', [{}])[0].get('text', ''),
                'description': json_data.get('descriptionSnippet', {}).get('runs', [{}])[0].get('text', ''),
                'published_time': parse_date_string(json_data.get('publishedTimeText', {}).get('simpleText', '')),
                'length_text': json_data.get('lengthText', {}).get('simpleText', ''),
                'view_count': int(json_data.get('viewCountText', {}).get('simpleText', '').split(' ')[0].replace(',', '')),
                'rich_thumbnail_url': json_data.get('richThumbnail', {}).get('movingThumbnailRenderer', {}).get('movingThumbnailDetails', {}).get('thumbnails', [{}])[0].get('url', ''),
                'resource_channel_id':json_data.get('resource_channel_id'),
                'channel_id':json_data.get('channel_id')
            }

            return video_data
        except Exception as e:
            return {}
        
class VideoMetric(Base):
    def __init__(self):
        __tablename__ = 'youtube_video_metrics'


        # Primary Key
        video_metric_id = Column(String, primary_key=True)
        created_at = Column(DateTime)
        channel_id = Column(String, ForeignKey('youtube_channel.channel_id'))
        video_id = Column(String, ForeignKey('youtube_video.video_id'))

        # metrics
        view_count = Column(Integer)
        comment_count = Column(Integer)
        like_count = Column(Integer)
        comment_sentiment = Column(Integer)
        retention_graph = Column(JSON)

        channel = relationship("Video", back_populates="video_metrics")
        video = relationship("Video", back_populates="metrics")



class Comment(Base):
    def __init__(self):
        pass
        #TODO implement