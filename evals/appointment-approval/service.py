from dataclasses import dataclass
import sqlite3


@dataclass(frozen=True)
class Actor:
    customer_id: str
    user_id: str
    role: str


def connect(path):
    database = sqlite3.connect(path)
    database.row_factory = sqlite3.Row
    return database


def init_db(database):
    database.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id TEXT PRIMARY KEY, customer_id TEXT NOT NULL,
        requester_id TEXT NOT NULL, starts_at TEXT NOT NULL
    )''')
    database.commit()


class AppointmentService:
    def __init__(self, database, mailer):
        self.database = database
        self.mailer = mailer

    def create(self, actor, appointment_id, starts_at):
        self.database.execute(
            'INSERT INTO appointments VALUES (?, ?, ?, ?)',
            (appointment_id, actor.customer_id, actor.user_id, starts_at),
        )
        self.database.commit()
        return appointment_id

    def list(self, actor):
        return [dict(row) for row in self.database.execute(
            'SELECT * FROM appointments WHERE customer_id = ? ORDER BY id',
            (actor.customer_id,),
        )]
