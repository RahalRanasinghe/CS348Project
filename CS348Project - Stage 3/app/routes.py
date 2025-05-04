from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, session
from .models import Customer, Organisation, Training, TrainingDetail, Exam, ExamDetail
from . import db
from datetime import datetime
from sqlalchemy import text
import io
import csv
import re
from functools import wraps


main = Blueprint('main', __name__)

def is_valid_ic(ic):
    return bool(re.fullmatch(r"\d{2}-\d{6}", ic))

def is_valid_phone(phone):
    return bool(re.fullmatch(r"\d{7}", phone))

def is_valid_email(email):
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

# Login page
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded users
        users = {
            "SynergyAdmin": {"password": "Synergy!321", "role": "admin"},
            "SynergyUser": {"password": "Synergy2025!", "role": "user"}
        }

        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('main.home'))
        else:
            flash("Invalid username or password", "danger")
            return render_template('login.html')
    return render_template('login.html')

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return wrapper



@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

# Homepage
@main.route('/')
@login_required
def home():
    return render_template('home.html')


# View all customers
@main.route('/customers')
def list_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)


# Adding new customer
@main.route('/customers/new', methods=["GET", "POST"])
@admin_required
def add_customer():
    if request.method == "POST":
        phone = request.form["PhoneNum"]
        ic = request.form["ICNum"]
        personal_email = request.form["PersonalEmail"]
        work_email = request.form["WorkEmail"]

        duplicate = False  # To determine if we should re-render the form

        # Validate formats
        if not is_valid_phone(phone):
            flash("Phone number must be exactly 7 digits (e.g., 7234342).", "danger")
            duplicate = True
        if not is_valid_ic(ic):
            flash("IC Number must be in the format NN-NNNNNN (e.g., 12-345678).", "danger")
            duplicate = True
        if not is_valid_email(personal_email):
            flash("Personal email must be a valid format and contain at least one '.' after '@'.", "danger")
            duplicate = True
        if not is_valid_email(work_email):
            flash("Work email must be a valid format and contain at least one '.' after '@'.", "danger")
            duplicate = True


        # Check for duplicates individually
        if Customer.query.filter_by(PhoneNum=phone).first():
            flash("A customer with this phone number already exists.", "danger")
            duplicate = True
        if Customer.query.filter_by(ICNum=ic).first():
            flash("A customer with this IC number already exists.", "danger")
            duplicate = True
        if Customer.query.filter_by(PersonalEmail=personal_email).first():
            flash("A customer with this personal email already exists.", "danger")
            duplicate = True
        if Customer.query.filter_by(WorkEmail=work_email).first():
            flash("A customer with this work email already exists.", "danger")
            duplicate = True

        if duplicate:
            organisations = Organisation.query.order_by(Organisation.OrganisationName).all()
            return render_template('customer_form.html', action='Add', organisations=organisations)

        # No issues found, then proceed to add
        new_customer = Customer(
            FirstName=request.form["FirstName"],
            LastName=request.form["LastName"],
            Gender=request.form["Gender"],
            DOB=datetime.strptime(request.form["DOB"], "%Y-%m-%d"),
            PhoneNum=phone,
            ICNum=ic,
            Organisation=request.form["Organisation"],
            PersonalEmail=personal_email,
            WorkEmail=work_email
        )
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('main.list_customers'))

    organisations = Organisation.query.order_by(Organisation.OrganisationName).all()
    return render_template('customer_form.html', action='Add', organisations=organisations)


# Edit existing customer
@main.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)

    if request.method == 'POST':
        phone = request.form["PhoneNum"]
        ic = request.form["ICNum"]
        personal_email = request.form["PersonalEmail"]
        work_email = request.form["WorkEmail"]

        duplicate = False

        # Input format validation
        if not is_valid_phone(phone):
            flash("Phone number must be exactly 7 digits (e.g., 7234342).", "danger")
            duplicate = True
        if not is_valid_ic(ic):
            flash("IC Number must be in the format NN-NNNNNN (e.g., 12-345678).", "danger")
            duplicate = True
        if not is_valid_email(personal_email):
            flash("Personal email must be a valid format and contain at least one '.' after '@'.", "danger")
            duplicate = True
        if not is_valid_email(work_email):
            flash("Work email must be a valid format and contain at least one '.' after '@'.", "danger")
            duplicate = True

        # Duplicate checks (excluding current customer ID)
        if Customer.query.filter(Customer.PhoneNum == phone, Customer.CustomerID != id).first():
            flash("Another customer already has this phone number.", "danger")
            duplicate = True
        if Customer.query.filter(Customer.ICNum == ic, Customer.CustomerID != id).first():
            flash("Another customer already has this IC number.", "danger")
            duplicate = True
        if Customer.query.filter(Customer.PersonalEmail == personal_email, Customer.CustomerID != id).first():
            flash("Another customer already has this personal email.", "danger")
            duplicate = True
        if Customer.query.filter(Customer.WorkEmail == work_email, Customer.CustomerID != id).first():
            flash("Another customer already has this work email.", "danger")
            duplicate = True

        if duplicate:
            organisations = Organisation.query.order_by(Organisation.OrganisationName).all()
            return render_template('customer_form.html', customer=customer, action='Edit', organisations=organisations)

        # No issues, update the customer
        customer.FirstName = request.form['FirstName']
        customer.LastName = request.form['LastName']
        customer.Gender = request.form['Gender']
        customer.DOB = datetime.strptime(request.form['DOB'], '%Y-%m-%d')
        customer.PhoneNum = phone
        customer.ICNum = ic
        customer.Organisation = request.form['Organisation']
        customer.PersonalEmail = personal_email
        customer.WorkEmail = work_email

        db.session.commit()
        return redirect(url_for('main.list_customers'))

    organisations = Organisation.query.order_by(Organisation.OrganisationName).all()
    return render_template('customer_form.html', customer=customer, action='Edit', organisations=organisations)


# Delete a customer
@main.route('/customers/delete/<int:id>', methods=['POST'])
@admin_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('main.list_customers'))

# Manage trainings
@main.route('/trainings')
def list_trainings():
    query = text("""
        SELECT t.TrainingID, t.CustomerID, c.FirstName, c.LastName, c.ICNum,
               t.TrainingDetailID, td.TrainingName, td.TrainingProvider,
               t.TrainingStartDate, t.TrainingEndDate
        FROM Trainings t
        JOIN CustomersPersonal c ON t.CustomerID = c.CustomerID
        JOIN TrainingsDetails td ON t.TrainingDetailID = td.TrainingDetailID
        ORDER BY t.TrainingID
    """)
    trainings = db.session.execute(query).fetchall()
    return render_template('trainings.html', trainings=trainings)

# Add training
@main.route('/trainings/new', methods=['GET', 'POST'])
@admin_required
def add_training():
    if request.method == 'POST':
        ic = request.form['ICNum']
        if not is_valid_ic(ic):
            flash("IC Number must be in the format NN-NNNNNN (e.g., 12-345678).", "danger")
            return redirect(url_for('main.add_training'))

        detail_id = request.form['TrainingDetailID']
        start_date = datetime.strptime(request.form['TrainingStartDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['TrainingEndDate'], '%Y-%m-%d').date()

        if start_date > end_date:
            flash("Start date cannot be after end date.", "danger")
            return redirect(url_for('main.add_training'))

        customer = Customer.query.filter_by(ICNum=ic).first()
        if not customer:
            flash("Customer with this IC number not found.", "danger")
            return redirect(url_for('main.add_training'))

        training = Training(
            CustomerID=customer.CustomerID,
            TrainingDetailID=detail_id,
            TrainingStartDate=start_date,
            TrainingEndDate=end_date
        )
        db.session.add(training)
        db.session.commit()
        return redirect(url_for('main.list_trainings'))

    training_details = TrainingDetail.query.order_by(TrainingDetail.TrainingName).all()
    return render_template('training_form.html', action='Add', training_details=training_details)

# Edit training
@main.route('/trainings/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_training(id):
    training = Training.query.get_or_404(id)

    if request.method == 'POST':
        ic = request.form['ICNum']
        if not is_valid_ic(ic):
            flash("IC Number must be in the format NN-NNNNNN (e.g., 12-345678).", "danger")
            return redirect(url_for('main.add_training'))

        detail_id = request.form['TrainingDetailID']
        start_date = datetime.strptime(request.form['TrainingStartDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['TrainingEndDate'], '%Y-%m-%d').date()

        if start_date > end_date:
            flash("Start date cannot be after end date.", "danger")
            return redirect(url_for('main.edit_training', id=id))

        customer = Customer.query.filter_by(ICNum=ic).first()
        if not customer:
            flash("Customer with this IC number not found.", "danger")
            return redirect(url_for('main.edit_training', id=id))

        training.CustomerID = customer.CustomerID
        training.TrainingDetailID = detail_id
        training.TrainingStartDate = start_date
        training.TrainingEndDate = end_date

        db.session.commit()
        return redirect(url_for('main.list_trainings'))

    # Prefill data
    training_details = TrainingDetail.query.order_by(TrainingDetail.TrainingName).all()
    customer = Customer.query.get(training.CustomerID)
    return render_template('training_form.html', action='Edit', training=training, customer=customer, training_details=training_details)

# Delete training
@main.route('/trainings/delete/<int:id>', methods=['POST'])
@admin_required
def delete_training(id):
    training = Training.query.get_or_404(id)
    db.session.delete(training)
    db.session.commit()
    flash("Training record deleted successfully.", "success")
    return redirect(url_for('main.list_trainings'))

# Manage exams
@main.route('/exams')
def list_exams():
    query = text("""
        SELECT 
            e.ExamID,
            e.CustomerID,
            c.FirstName,
            c.LastName,
            c.ICNum,
            e.ExamDetailID,
            ed.ExamName,
            ed.ExamProvider,
            e.ExamDate
        FROM Exams e
        JOIN CustomersPersonal c ON e.CustomerID = c.CustomerID
        JOIN ExamsDetails ed ON e.ExamDetailID = ed.ExamDetailID
        ORDER BY e.ExamID
    """)
    exams = db.session.execute(query).fetchall()
    return render_template('exams.html', exams=exams)

# Add exams
@main.route('/exams/new', methods=['GET', 'POST'])
@admin_required
def add_exam():
    if request.method == 'POST':
        ic = request.form['ICNum']
        detail_id = request.form['ExamDetailID']
        exam_date = datetime.strptime(request.form['ExamDate'], '%Y-%m-%d').date()

        customer = Customer.query.filter_by(ICNum=ic).first()
        if not customer:
            flash("Customer with this IC number not found.", "danger")
            return redirect(url_for('main.add_exam'))

        new_exam = Exam(
            CustomerID=customer.CustomerID,
            ExamDetailID=detail_id,
            ExamDate=exam_date
        )
        db.session.add(new_exam)
        db.session.commit()
        return redirect(url_for('main.list_exams'))

    exam_details = ExamDetail.query.order_by(ExamDetail.ExamName).all()
    return render_template('exam_form.html', action='Add', exam_details=exam_details)

# Edit exam
@main.route('/exams/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_exam(id):
    exam = Exam.query.get_or_404(id)

    if request.method == 'POST':
        ic = request.form['ICNum']
        detail_id = request.form['ExamDetailID']
        exam_date = datetime.strptime(request.form['ExamDate'], '%Y-%m-%d').date()

        customer = Customer.query.filter_by(ICNum=ic).first()
        if not customer:
            flash("Customer with this IC number not found.", "danger")
            return redirect(url_for('main.edit_exam', id=id))

        exam.CustomerID = customer.CustomerID
        exam.ExamDetailID = detail_id
        exam.ExamDate = exam_date

        db.session.commit()
        return redirect(url_for('main.list_exams'))

    customer = Customer.query.get(exam.CustomerID)
    exam_details = ExamDetail.query.order_by(ExamDetail.ExamName).all()
    return render_template('exam_form.html', action='Edit',  exam=exam, customer=customer, exam_details=exam_details)

# Delete exam
@main.route('/exams/delete/<int:id>', methods=['POST'])
@admin_required
def delete_exam(id):
    exam = Exam.query.get_or_404(id)
    db.session.delete(exam)
    db.session.commit()
    return redirect(url_for('main.list_exams'))

# Get customer name
@main.route('/get-customer-name')
def get_customer_name():
    ic = request.args.get('ic')
    customer = Customer.query.filter_by(ICNum=ic).first()
    if customer:
        return {'first_name': customer.FirstName, 'last_name': customer.LastName}
    else:
        return {}, 404
"""
____________________________________________________________________________________________________________________________________________________________________________________________________________________
"""
# Requirement 2
# Reports
@main.route('/reports', methods=['GET'])
def reports():
    return render_template('reports.html')


@main.route('/reports/results', methods=['POST'])
def report_results():
    # Display date range at the top of the report at dd/mm/yyyy
    start_date_str = request.form['start_date']
    end_date_str = request.form['end_date']
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    report_type = request.form['report_type']

    if start_date > end_date:
        flash("Start date cannot be after end date. Please select a valid date range.", "danger")
        return redirect(url_for('main.reports'))

    results = []

    if report_type == 'exams':
        query = text("""
            SELECT 
                e.ExamDate, ed.ExamName, ed.ExamProvider, ed.NumHours,
                c.FirstName, c.LastName, c.ICNum, c.Organisation, c.WorkEmail
            FROM Exams e
            JOIN ExamsDetails ed ON e.ExamDetailID = ed.ExamDetailID
            JOIN CustomersPersonal c ON e.CustomerID = c.CustomerID
            WHERE e.ExamDate BETWEEN :start AND :end
            ORDER BY e.ExamDate
        """)
    else:
        query = text("""
            SELECT 
                t.TrainingStartDate, t.TrainingEndDate, td.TrainingName,
                td.TrainingProvider, td.NumHours,
                c.FirstName, c.LastName, c.ICNum, c.Organisation, c.WorkEmail
            FROM Trainings t
            JOIN TrainingsDetails td ON t.TrainingDetailID = td.TrainingDetailID
            JOIN CustomersPersonal c ON t.CustomerID = c.CustomerID
            WHERE 
                t.TrainingEndDate >= :start AND t.TrainingStartDate <= :end
            ORDER BY t.TrainingStartDate
        """)

    results = db.session.execute(query, {"start": start_date, "end": end_date}).fetchall()

    if not results:
        flash(f"No {report_type} found in the selected date range. Please try a different range.", "warning")
        return redirect(url_for('main.reports'))

    return render_template('report_results.html',
                           report_type=report_type,
                           results=results,
                           start_date=start_date,
                           end_date=end_date)


# Export as a CSV
@main.route('/export/csv', methods=['POST'])
def export_csv():
    report_type = request.form['report_type']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

    if report_type == 'exams':
        query = text("""
            SELECT 
                e.ExamDate, ed.ExamName, ed.ExamProvider, ed.NumHours,
                c.FirstName, c.LastName, c.ICNum, c.Organisation, c.WorkEmail
            FROM Exams e
            JOIN ExamsDetails ed ON e.ExamDetailID = ed.ExamDetailID
            JOIN CustomersPersonal c ON e.CustomerID = c.CustomerID
            WHERE e.ExamDate BETWEEN :start AND :end
            ORDER BY e.ExamDate
        """)
        headers = ['Exam Date', 'Exam Name', 'Provider', 'Hours', 'Customer Name', 'IC Number', 'Organisation', 'Work Email']
    else:
        query = text("""
            SELECT 
                t.TrainingStartDate, t.TrainingEndDate, td.TrainingName,
                td.TrainingProvider, td.NumHours,
                c.FirstName, c.LastName, c.ICNum, c.Organisation, c.WorkEmail
            FROM Trainings t
            JOIN TrainingsDetails td ON t.TrainingDetailID = td.TrainingDetailID
            JOIN CustomersPersonal c ON t.CustomerID = c.CustomerID
            WHERE 
                t.TrainingEndDate >= :start AND t.TrainingStartDate <= :end
            ORDER BY t.TrainingStartDate
        """)
        headers = ['Start Date', 'End Date', 'Training Name', 'Provider', 'Hours', 'Customer Name', 'IC Number', 'Organisation', 'Work Email']

    results = db.session.execute(query, {"start": start_date, "end": end_date}).fetchall()

    start_str = start_date.strftime('%d-%m-%y')
    end_str = end_date.strftime('%d-%m-%y')
    filename = f"{report_type.capitalize()} from {start_str} to {end_str}.csv"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for row in results:
        if report_type == 'exams':
            writer.writerow([
                row.ExamDate.strftime('%d/%m/%Y'),
                row.ExamName,
                row.ExamProvider,
                row.NumHours,
                f"{row.FirstName} {row.LastName}",
                row.ICNum,
                row.Organisation,
                row.WorkEmail
            ])
        else:
            writer.writerow([
                row.TrainingStartDate.strftime('%d/%m/%Y'),
                row.TrainingEndDate.strftime('%d/%m/%Y'),
                row.TrainingName,
                row.TrainingProvider,
                row.NumHours,
                f"{row.FirstName} {row.LastName}",
                row.ICNum,
                row.Organisation,
                row.WorkEmail
            ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    return response

