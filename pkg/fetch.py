import json, os
from pyyoutube import Client, Api
from slugify import slugify
import scrapetube
import logging
from sqlalchemy import select, create_engine, URL
from sqlalchemy.orm import Session
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from .models import Channel, Video, Subscription
from .util import genv
import sys
import asyncio
from aiomultiprocess import Pool
# from aiostream import stream, pipe
# from aiohttp import request
import pandas as pd


#TODO implement better metrics functionalityy
def fetch_channel_videos(
    c_,
    r_=0,
    videos=[],
    max_retires=3,
    force=False
):
    """
    Fetches all videos that belong to a given youtube channel
    :param engine:
    :param api_key:
    :param max_retires:
    :param c_:
    :param r_:
    :param force:
    :return:
    """
    r_+=1
    r, c, v_ = str(r_), str(c_), 0
    try:
        print(f"Fetching videos for {c}")
        for video_data in scrapetube.get_channel(c_) :
            try:
                video_data["resource_channel_id"] = c_
                videos.append(video_data)
                v_+=1
                if v_%100==0:print(v_)
            except Exception as e:
                logging.exception(e)
        print(f"Successfully fetched {str(len(videos))} videos.")
    except Exception as e:
        logging.exception(e)
        if r_ <= max_retires:
            logging.warn(f"fetch {c} failed {r} times, retrying")
            return fetch_channel_videos(c_, r_, videos=videos)
    return c_, videos



async def _fetch(c):
    try:
        api_key = genv("API_KEY")
        db_user = genv("DB_USERNAME")
        db_host = genv("DB_HOST")
        db_name = genv("DB_NAME")
        db_pass = genv("DB_PASS")
        sec_file = genv("CLIENT_SECRETS_FILE")

        url = URL.create(
            drivername="postgresql",
            username=db_user,
            host=db_host,
            database=db_name,
            password=db_pass
        )

        engine = create_engine(url)

        with Session(engine) as session:
            _, videos = fetch_channel_videos(
                c,
                max_retires=3
            )
            print(f"Removing duplicates from {c}")
            videos = pd.DataFrame([Video.extract(v) for v in videos]).drop_duplicates(subset=['video_id']).to_dict('records')
            print(f"Persissting {str(len(videos))} videos.")
            for v in videos:
                try:
                    vid = session.query(Video).filter_by(video_id=v['video_id']).first()
                    if not vid: session.add(Video(**v))
                except Exception as e:
                    logging.exception(e)
                    session.rollback()

            session.commit()
            print(f"{str(len(videos))} videos persisted.")
    except Exception as e:
        session.rollback()
        logging.exception(e)

async def fetch_all_videos_from_channels_async(
    engine,
    api_key,
    max_retires=3,
):
    with Session(engine) as session:
       cids =  [c.resource_channel_id for c in session.scalars(select(Subscription))]
    print(cids)
    async with Pool() as pool:
        async for _ in pool.map(_fetch, cids):
            print("persisted all videos")


def fetch_subscribed_channels(
    engine,
    client_secrets_file,
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"],
    api_service_name = "youtube",
    api_version = "v3",
    insecure_transport=True,
    max_results=50,
    is_mine=True,
    max_retries=3,
    r_=0,
):
    if not isinstance(client_secrets_file, str):
        raise ValueError("please set a google client secrets file for fetching subscriptions")

    if not os.path.exists(client_secrets_file):
        raise ValueError("google client secrets file for fetching subscriptions does not exist")

    if insecure_transport:
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        scopes,
    )
    credentials = flow.run_console()

    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        credentials=credentials
    )

    cont_, pageToken, tc_ = True, None, 0

    with Session(engine) as session:
        try:
            while cont_:
                try:
                        r_ += 1
                        request = youtube.subscriptions().list(
                            part="snippet,contentDetails",
                            pageToken=pageToken,
                            maxResults=max_results,
                            mine=is_mine
                        )
                        response = request.execute()
                        items = [Subscription(item_) for item_ in response["items"]]
                        for v in items:
                            try:
                                vid = session.query(Subscription).filter_by(resource_channel_id=v.resource_channel_id).first()
                                if not vid: session.add(v)
                            except Exception as e:
                                session.rollback()

                        m=f"Persisted {str(len(items))} subscriptions"
                        logging.info(m)
                        print(m, flush=True)
                        tc_ += len(items)

                        if "nextPageToken" in response:
                            pageToken = response['nextPageToken']
                        else:
                            cont_ = False
                            m=f"Successfully persisted all {str(tc_)} subscriptions"
                            logging.info(m)
                            print(m, flush=True)


                except Exception as e:
                    logging.exception(e)
                    if r_ > max_retries:
                        m=f"fetch subscriptions failed {str(r_)} times, retrying"
                        print(m, flush=True)
                        cont_ = False

            session.commit()
        except Exception as e:
           session.rollback()


