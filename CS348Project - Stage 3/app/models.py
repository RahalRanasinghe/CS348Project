from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config

from . import db

app = Flask(__name__)
app.config.from_object(Config)


# db = SQLAlchemy(app)


# Customer Model
class Customer(db.Model):
    __tablename__ = "CustomersPersonal"

    CustomerID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(25), nullable=False)
    LastName = db.Column(db.String(25), nullable=False)
    Gender = db.Column(db.String(1), nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    PhoneNum = db.Column(db.String(7), nullable=False)
    ICNum = db.Column(db.String(9), unique=True, nullable=False)
    Organisation = db.Column(db.String(100), nullable=False)
    PersonalEmail = db.Column(db.String(100), nullable=False)
    WorkEmail = db.Column(db.String(100), nullable=False)


# Organisation Model for drop-down menu in customer_form page
class Organisation(db.Model):
    __tablename__ = "OrganisationList"
    OrganisationID = db.Column(db.Integer, primary_key=True)
    OrganisationName = db.Column(db.String(100), nullable=False, unique=True)

# Training Model
class Training(db.Model):
    __tablename__ = "Trainings"
    TrainingID = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey("CustomersPersonal.CustomerID"))
    TrainingDetailID = db.Column(db.Integer, db.ForeignKey("TrainingsDetails.TrainingDetailID"))
    TrainingStartDate = db.Column(db.Date, nullable=False)
    TrainingEndDate = db.Column(db.Date, nullable=False)

    customer = db.relationship("Customer", backref="trainings")
    detail = db.relationship("TrainingDetail", backref="instances")

# TrainingDetail Model
class TrainingDetail(db.Model):
    __tablename__ = "TrainingsDetails"
    TrainingDetailID = db.Column(db.Integer, primary_key=True)
    TrainingName = db.Column(db.String(100), nullable=False)
    TrainingProvider = db.Column(db.String(100), nullable=False)
    NumHours = db.Column(db.Integer, nullable=False)

# Exam Model
class Exam(db.Model):
    __tablename__ = "Exams"
    ExamID = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey("CustomersPersonal.CustomerID"))
    ExamDetailID = db.Column(db.Integer, db.ForeignKey("ExamsDetails.ExamDetailID"))
    ExamDate = db.Column(db.Date, nullable=False)

    customer = db.relationship("Customer", backref="exams")
    detail = db.relationship("ExamDetail", backref="instances")

# ExamDetail Model
class ExamDetail(db.Model):
    __tablename__ = "ExamsDetails"
    ExamDetailID = db.Column(db.Integer, primary_key=True)
    ExamName = db.Column(db.String(100), nullable=False)
    ExamProvider = db.Column(db.String(100), nullable=False)
    NumHours = db.Column(db.Integer, nullable=False)

@app.route("/")
def home():
    return render_template("base.html")
