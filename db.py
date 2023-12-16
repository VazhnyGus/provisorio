import sqlite3 as sq
from typing import List, Tuple, Dict
from datetime import date


def initiate_db():
    with sq.connect("drugs.db") as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS drugs(
            id INTEGER NOT NULL UNIQUE,
            user TEXT NOT NULL,
            drug TEXT NOT NULL,
            exp_date INTEGER NOT NULL,
            PRIMARY KEY("id")
        )""")


def db_add_drug(user: str, drug: str, exp_date: int) -> None:
    with sq.connect("drugs.db") as db:
        c = db.cursor()
        c.execute(f"INSERT INTO drugs (user, drug, exp_date) VALUES ('{user}', '{drug}', '{exp_date}')")


def db_delete_drug(db_id: int) -> None:
    with sq.connect("drugs.db") as db:
        c = db.cursor()
        c.execute(f"DELETE FROM drugs WHERE id={db_id}")


def db_get_user_drugs(user: str) -> List[Tuple[int, str, int]]:
    with sq.connect("drugs.db") as db:
        c = db.cursor()
        c.execute(f"SELECT id, drug, exp_date FROM drugs WHERE user='{user}' ORDER BY id")
        return c.fetchall()


def db_get_overdue() -> Dict[str, List[Tuple[str, int]]]:
    now = date.today().toordinal()
    with sq.connect("drugs.db") as db:
        c = db.cursor()
        c.execute(f"SELECT DISTINCT user FROM drugs WHERE exp_date < {now}")
        users = c.fetchall()
        overdue = {}
        for user in users:
            c.execute(f"SELECT drug, exp_date FROM drugs WHERE user='{user[0]}' AND exp_date < {now}")
            od_drugs = c.fetchall()
            od_list = []
            for od_drug in od_drugs:
                od_list.append(od_drug)
            overdue.update({user[0]: od_list})
        return overdue


def db_delete_overdue(user: str) -> None:
    now = date.today().toordinal()
    with sq.connect("drugs.db") as db:
        c = db.cursor()
        c.execute(f"DELETE FROM drugs WHERE user='{user}' AND exp_date < {now}")
