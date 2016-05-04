# Lionel

Lionel is a Django based web-app which takes delimited files and runs standard (user-defined) processes on them within a database.

## setup

We will eventually build a script for this but it isn't a focus right now.

For now you need python 3.4+.

Run pip install -r requirements.txt

Copy the example_settings.py file into a settings.py file and give it a secret key.

To run:

python manage.py runserver

You will then be able to access the program from localhost:8000/loader

## History

We found at work that a lot of what we were doing was loading new data feeds and adapting them to existing processes via standard ETL.

A few of us wanted to make a small in-house solution for this which would run the processes we normally hook up to the data.

As an evolution of the idea we wanted to see how flexible we could make it, whilst keeping it secure and usable.

It is highly likely something similar exists, but we like building software.

## Roadmap

Lionel is in active development, and whenever we have time we try to add to the project.

### 0.1

* Basic user system.
* Feed adding through admin.
* File processing.
* Functioning for at least one RDBMS (probably postgres or oracle).

###0.2

* File analysis.

### 1.0

* Functioning for all major RDBMS.
* Full-fledged user system.
* Data feed management.
* Adh-hoc data processing.
* Flexibility in adding new processes
* External and internal users.
