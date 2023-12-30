# with Session(engine) as session:
#     async with Pool() as pool:
#         async for result in pool.map(fetch_channel_videos,
#                                      [c.resource_channel_id for c in session.scalars(select(Subscription))]):
#             _, videos = result
#             videos = pd.DataFrame([Video.extrtact(v) for v in videos]).drop_duplicates(subset=['video_id']).to_dict(
#                 'records')
#             print(videos[0])
#             session.add_all([Video(**v) for v in videos])
#             session.commit()
#             print("persisted all videos")

#
# def fetch_and_persist_channel():
#     logging.info("Fetching {c}")
#     print(c_)
#     api = Api(api_key=api_key)
#     channel_by_id = api.get_channel_info(channel_id=c_)
#     channel_data = channel_by_id.items[0].to_dict()
#     with Session(engine) as session:
#         session.add_all([channel])
#         session.add_all(videos_)
#         session.commit()
#         channel = Channel(channel_data)
#         channel.slug = slugify(channel_data['snippet']['title'])
#         channel.cid = slugify(c_)
#         channel.pname = f'{channel.slug}_{channel.cid}'
#     pass
#
# def fetch_all_videos_from_channels(
#     engine,
#     api_key,
#     max_retires=3,
# ):
#     with Session(engine) as session:
#         for c in session.scalars(select(Subscription)):
#             _, videos = fetch_channel_videos(
#                 c.resource_channel_id,
#                 max_retires=max_retires
#             )
#             try:
#                 videos = pd.DataFrame([Video.extract(v) for v in videos]).drop_duplicates(subset=['video_id']).to_dict('records')
#                 print(videos[0])
#                 for v in videos:
#                     try:
#                         vid = session.query(Video).filter_by(video_id=v['video_id']).first()
#                         if not vid:session.add(Video(**v))
#                     except Exception as e:
#                         logging.exception(e)
#                 session.commit()
#                 print("persisted all videos")
#             except Exception as e:
#                 logging.exception(e)