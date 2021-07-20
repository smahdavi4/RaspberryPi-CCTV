import threading

from peewee import Model, CharField, BooleanField, SqliteDatabase, Metadata, TimeField

db = SqliteDatabase('cctv.db')


class ThreadSafeDatabaseMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        # database attribute is stored in a thread-local.
        self._local = threading.local()
        super(ThreadSafeDatabaseMetadata, self).__init__(*args, **kwargs)

    def _get_db(self):
        return getattr(self._local, 'database', self._database)

    def _set_db(self, db):
        self._local.database = self._database = db

    database = property(_get_db, _set_db)


class Users(Model):
    chat_id = CharField(max_length=50, unique=True)
    otp = CharField(max_length=100)
    is_active = BooleanField(default=False)

    class Meta:
        model_metadata_class = ThreadSafeDatabaseMetadata
        database = db


class Schedules(Model):
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    All = "All"
    WEEKDAYS = (
        Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, All
    )

    weekday = CharField(max_length=20, choices=WEEKDAYS)
    start_time = TimeField()
    end_time = TimeField()

    def __repr__(self):
        return f"{self.id} - {str(self.start_time)[:5]} - {str(self.end_time)[:5]} - {self.weekday}"

    class Meta:
        model_metadata_class = ThreadSafeDatabaseMetadata
        database = db


def init_db():
    db.create_tables([Users, Schedules], safe=True)
