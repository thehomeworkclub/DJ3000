from peewee import * 

db = SqliteDatabase('db.db')

class Segments(Model):
    segment_name = CharField()
    session_id = UUIDField()
    time_start = IntegerField()
    time_end = IntegerField()
    last_song_index = IntegerField()
    class Meta:
        database = db
        