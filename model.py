from peewee import * 
import os
from dotenv import load_dotenv
load_dotenv()

db = PostgresqlDatabase('segments', user="segments_owner", password=os.environ.get("PG_PASS"), host="ep-little-union-a682nje5.us-west-2.aws.neon.tech?sslmode=require")

class Segments(Model):
    id = AutoField()
    segment_name = CharField()
    session_id = UUIDField()
    time_start = IntegerField()
    time_end = IntegerField()
    last_song_index = IntegerField()
    class Meta:
        database = db
        