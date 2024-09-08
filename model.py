from peewee import * 
import os
from dotenv import load_dotenv
load_dotenv()

# Get the endpoint ID from the Neon connection string
endpoint_id = "ep-little-union-a682nje5"

# Construct the new connection string
db = PostgresqlDatabase(
    f"segments?options=endpoint%3D{endpoint_id}",
    user="segments_owner",
    password=os.environ.get("PG_PASS"),
    host=f"{endpoint_id}.us-west-2.aws.neon.tech",
    sslmode="require"
)

class Segments(Model):
    id = AutoField()
    segment_name = CharField()
    session_id = UUIDField()
    time_start = IntegerField()
    time_end = IntegerField()
    last_song_index = IntegerField()
    class Meta:
        database = db
        