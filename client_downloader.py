from model import *
import os
import time
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client(
    service_name ="s3",
    endpoint_url = os.environ.get("S3_BUCKET"),
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="auto", # Must be one of: wnam, enam, weur, eeur, apac, auto
)

LAST_SEGMENT_PLAYED = 0
SESSION_ID = ""
segments_in_local = []
frequency = 97.5

while True:
    while True:
        segments = Segments.select()
        if len(segments) == 0:
            print("Waiting for segments to be added to the database...", end="\r")
            time.sleep(1)
        elif len(segments) == len(segments_in_local) and SESSION_ID == segments[0].session_id:
            print("Waiting for new segments to be added to the database...", end="\r")
            time.sleep(1)
        else:
            segments_in_local = segments
            SESSION_ID = segments[0].session_id
            print("Found segments: " + str(len(segments_in_local)))
            break
    for segment in segments_in_local:
        if segment.id > LAST_SEGMENT_PLAYED:
            print("Downloading segment %s" % segment.segment_name)
            s3.download_file("dj3000", f"{segment.segment_name}.wav", f"segment_{segment.id}.wav")
            LAST_SEGMENT_PLAYED = segment.id
            print("Segment %s finished downloading" % segment.segment_name)
        time.sleep(1)