from model import *
import os
import time

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
            print("Playing segment %s" % segment.segment_name)
            LAST_SEGMENT_PLAYED = segment.id
            os.system(f"sudo ./fm_transmitter/fm_transmitter -f {frequency} -b 300 segment_{segment.id}.wav")
        time.sleep(1)