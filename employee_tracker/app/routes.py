from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import db, User, PunchLog
from datetime import datetime, timedelta

# Setup Blueprint
main = Blueprint('main', __name__)

# Helper to check if current user is admin
def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

# Home redirects to login
@main.route('/')
def home():
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    today = datetime.today().date()

    # Calculate the date for two weeks ago
    two_weeks_ago = today - timedelta(weeks=2)

    # Query logs for the current user from the last two weeks
    logs = PunchLog.query.filter(
        PunchLog.user_id == current_user.id,
        PunchLog.date >= two_weeks_ago  # Filter for logs within the last two weeks
    ).order_by(PunchLog.date.asc()).all()

    # Calculate total hours worked for the employee
    total_hours = 0
    for log in logs:
        if log.punch_in and log.punch_out:
            punch_in_time = log.punch_in
            punch_out_time = log.punch_out
            worked_hours = (punch_out_time - punch_in_time).total_seconds() / 3600  # Convert seconds to hours
            total_hours += worked_hours
    total_hours = round(total_hours, 2)
    # Check if the user is punched in
    latest_log = PunchLog.query.filter_by(user_id=current_user.id, date=today).order_by(PunchLog.id.desc()).first()
    is_punched_in = False
    if latest_log and latest_log.punch_in and not latest_log.punch_out:
        is_punched_in = True

    return render_template('dashboard.html', logs=logs, is_punched_in=is_punched_in, total_hours=total_hours)

# Punch In Route (Only for employees)
@main.route('/punch_in', methods=['POST'])
@login_required
def punch_in():
    if not is_admin():  # Prevent admin from punching in
        today = datetime.today().date()
        new_log = PunchLog(user_id=current_user.id, date=today, punch_in=datetime.now())
        db.session.add(new_log)
        db.session.commit()
    return redirect(url_for('main.dashboard'))

# Punch Out Route (Only for employees)
@main.route('/punch_out', methods=['POST'])
@login_required
def punch_out():
    if not is_admin():  # Prevent admin from punching out
        today = datetime.today().date()
        latest_log = PunchLog.query.filter_by(user_id=current_user.id, date=today).order_by(PunchLog.id.desc()).first()

        if latest_log and latest_log.punch_in and not latest_log.punch_out:
            latest_log.punch_out = datetime.now()
            db.session.commit()
    return redirect(url_for('main.dashboard'))

# Admin Dashboard with filters
@main.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not is_admin():
        return "Unauthorized", 403

    filter_type = request.args.get('filter', 'all')
    logs_query = PunchLog.query.join(User).filter(User.role == 'employee')
    today = datetime.today().date()

    # Filters for logs
    if filter_type == 'today':
        logs_query = logs_query.filter(PunchLog.date == today)
    elif filter_type == 'week':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        logs_query = logs_query.filter(PunchLog.date.between(start, end))
    elif filter_type == 'month':
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        logs_query = logs_query.filter(PunchLog.date.between(start, end))
    elif filter_type == 'custom' and request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date and end_date:
            logs_query = logs_query.filter(PunchLog.date.between(start_date, end_date))

    logs = logs_query.order_by(PunchLog.date.asc()).all()

    # Calculate total hours worked for each employee
    employee_hours = {}
    total_hours = 0
    for log in logs:
        if log.user_id not in employee_hours:
            employee_hours[log.user_id] = 0
        if log.punch_in and log.punch_out:
            punch_in_time = log.punch_in
            punch_out_time = log.punch_out
            worked_hours = (punch_out_time - punch_in_time).total_seconds() / 3600  # Convert seconds to hours
            employee_hours[log.user_id] += worked_hours
            total_hours += worked_hours  # Sum up total hours worked across all logs

    # Get all employees for the graph and modify view
    employees = User.query.filter_by(role='employee').all()

    # Render the template and pass the necessary data
    return render_template('admin_dashboard.html', logs=logs, filter_type=filter_type,
                           employee_hours=employee_hours, employees=employees, total_hours=total_hours)


# Modify Punch Route
@main.route('/modify_punch/<int:log_id>', methods=['GET', 'POST'])
@login_required
def modify_punch(log_id):
    if not is_admin():
        return "Unauthorized", 403

    log = PunchLog.query.get_or_404(log_id)

    if request.method == 'POST':
        # Handle modification here (e.g., update punch-in or punch-out times)
        punch_in_time = request.form['punch_in']
        punch_out_time = request.form['punch_out']

        # Convert the input times to datetime format
        if punch_in_time:
            log.punch_in = datetime.strptime(punch_in_time, '%Y-%m-%dT%H:%M')
        if punch_out_time:
            log.punch_out = datetime.strptime(punch_out_time, '%Y-%m-%dT%H:%M')

        db.session.commit()
        flash('Punch record updated successfully.', 'success')
        return redirect(url_for('main.admin_dashboard'))

    # Render the template with the punch log for editing
    return render_template('modify_punch.html', log=log)
