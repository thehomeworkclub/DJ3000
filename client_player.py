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
        while True:
            if os.path.exists(f"segment_{segment.id}.wav"):
                break
        if segment.id > LAST_SEGMENT_PLAYED:
            print("Playing segment %s" % segment.segment_name)
            LAST_SEGMENT_PLAYED = segment.id
            os.system(f"sudo /home/pi/fm_transmitter/fm_transmitter -f {frequency} -b 300 segment_{segment.id}.wav")
            # remove the file after playing
            os.remove(f"segment_{segment.id}.wav")
            s3.delete_object(Bucket="dj3000", Key=f"{segment.segment_name}.wav")
            print("Segment %s finished" % segment.segment_name)
        time.sleep(1)