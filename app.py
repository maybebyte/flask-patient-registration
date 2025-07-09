#!/usr/bin/env python3

import sqlite3
from datetime import datetime

from flask import Flask, g, render_template, request

DATABASE_FILE = "patients.db"
SCHEMA_FILE = "schema.sql"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_FILE)
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(SCHEMA_FILE) as f:
            db.cursor().executescript(f.read().decode("utf-8"))
        db.commit()


app = Flask(__name__)
init_db()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET"])
def display_form():
    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("form.html", today=today)


@app.route("/submit", methods=["POST"])
def submit():
    form_fields = [
        "first_name",
        "last_name",
        "date_of_birth",
        "therapist_name",
    ]

    patient_data = {}
    today = datetime.today().strftime("%Y-%m-%d")

    for form_field in form_fields:
        field_value = request.form.get(form_field, "")
        field_value = field_value.strip()

        if not field_value:
            return render_template(
                "form.html", error="Please fill in all fields.", today=today
            )

        patient_data[form_field] = field_value

    try:
        birth_date = datetime.strptime(
            patient_data["date_of_birth"], "%Y-%m-%d"
        ).date()

        if birth_date > datetime.today().date():
            return render_template(
                "form.html", error="Invalid birth date.", today=today
            )
    except ValueError:
        return render_template(
            "form.html", error="Invalid birth date.", today=today
        )

    db = get_db()
    db.execute(
        "INSERT INTO patients (first_name, last_name, date_of_birth, therapist_name) VALUES (?, ?, ?, ?)",
        (
            patient_data["first_name"],
            patient_data["last_name"],
            patient_data["date_of_birth"],
            patient_data["therapist_name"],
        ),
    )
    db.commit()

    return render_template(
        "confirmation.html",
        first_name=patient_data["first_name"],
        last_name=patient_data["last_name"],
        date_of_birth=patient_data["date_of_birth"],
        therapist_name=patient_data["therapist_name"],
    )
