import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://sqlAdmin:Synergy%21@synergy-skills-server.database.windows.net/'
        'synergy_skills?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flash message for when there are no records for reports being genereated
    SECRET_KEY = "synergy_skills_2025"

    # New line for session timeout
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)