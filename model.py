from peewee import * 
import os
from dotenv import load_dotenv
load_dotenv()

db = PostgresqlDatabase('d3rgplacpflhq4', user="u3inloif293kd5", password=os.environ.get("PG_PASS"), port=5432, host="c5flugvup2318r.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com", sslmode="require")

class Segments(Model):
    id = AutoField()
    segment_name = CharField()
    session_id = UUIDField()
    time_start = IntegerField()
    time_end = IntegerField()
    last_song_index = IntegerField()
    class Meta:
        database = db
        
db.connect()
db.create_tables([Segments])