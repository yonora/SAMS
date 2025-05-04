from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session, jsonify
from flask_login import LoginManager, UserMixin, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
import os
import pandas as pd

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
# Add a secret key for Flask sessions and flash messages
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key_for_development')

# Initialize Flask-Login for user authentication
login_manager = LoginManager()
login_manager.init_app(app)

# Configure MySQL connection using environment variables
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Create User class
class User(UserMixin):
    def __init__(self, user_id, email, role):
        self.id = user_id
        self.email = email
        self.role = role

# Retrieve the logged-in user
@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id, email, role FROM users WHERE id=%s", (user_id,))
    admin = cursor.fetchone()
    cursor.close()
    db.close()

    if admin:
        return User(user_id=admin[0], email=admin[1], role=admin[2])
    return None  # If no user found

# Check if the user is authenticated and admin
def authorize():
    return current_user.is_authenticated and current_user.role == 'admin'

# Render Home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle admin login page rendering and authentication process (using flask-login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login request
    if request.method == 'POST':
        db = get_db_connection()
        cursor = db.cursor()

        email = request.form['email']
        password = request.form['password']

        # Retrieve user account with the given email
        cursor.execute("SELECT id, email, password, role FROM users WHERE email=%s", (email,))
        user_data = cursor.fetchone()

        # Check if user exists and validate passsword
        if user_data:
            if check_password_hash(user_data[2], password):
                user = User(user_id=user_data[0], email=user_data[1], role=user_data[3])
                login_user(user) 
                return redirect(url_for('index'))
            else:
                flash('Incorrect Password!', 'error')
        else:
            flash('User not found!', 'error')
        
        # Re-render login page with error message
        return render_template('login.html')
    
    # Render login page
    return render_template('login.html')

# Handle student login page rendering and authentication process (using session to store student id)
# To ensure that they can only view their data
@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    # Handle login request
    if request.method == 'POST':
        db = get_db_connection()
        cursor = db.cursor()
        student_id = request.form['student_id']

        # Retrieve student information with the given student_id
        cursor.execute("SELECT student_id FROM student WHERE student_id=%s", (student_id,))
        student_data = cursor.fetchone()

        # Check if student exist
        if not student_data:
            flash('Student not found!', 'error')
            return render_template('student_login.html')
        
        # Saving the student id in the session
        session['student_id'] = student_data[0]

        flash('Logged In!', 'success')
        return redirect(url_for('index'))
    
    # Render login page
    return render_template('student_login.html')

# Handle user logout
@app.route("/logout")
def logout():
    # Student logout
    if session.get('student_id'):
        session.pop('student_id')
    else:
        logout_user() # Admin logout

    return redirect(url_for('index'))

# Students Management
# Display students info in the table
@app.route('/students', methods=['GET', 'POST'])
def students():
    db = get_db_connection()
    cursor = db.cursor()
    if request.method == 'POST':
        # Handle form submission from modal
        return redirect(url_for('students'))
    cursor.execute("SELECT * FROM student")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('student_info.html', data=data)

# Store student info in the database
@app.route('/students/add', methods=['POST']) 
def add_student():
    # Get form data
    student_id = request.form['student_id']
    student_name = request.form['student_name']
    year_section = request.form['year_section']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO student (student_id, student_name, year_section) VALUES (%s, %s, %s)",
        (student_id, student_name, year_section))
    db.commit()
    cursor.close()
    db.close()

    flash('Student information successfully added!', 'success')
    return redirect(url_for('students'))

# Update student info in the database
@app.route('/students/<int:id>/edit', methods=['POST'])
def edit_student(id):
    # Get form data
    student_id = request.form['student_id']
    student_name = request.form['student_name']
    year_section = request.form['year_section']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE student SET student_id=%s, student_name=%s, year_section=%s WHERE id=%s",
        (student_id, student_name, year_section, id))
    db.commit()
    cursor.close()
    db.close()

    flash('Student information successfully updated!', 'success')
    return redirect(url_for('students'))

# Delete student info
@app.route('/students/<int:id>/delete')
def delete_student(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM student WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Student information successfully deleted!', 'success')
    return redirect(url_for('students'))

# Attendance Management
# Display attendance data in the table
@app.route('/attendance', methods=['GET', 'POST']) 
def attendance():
    admin = authorize()
    if request.method == 'POST':
        # Handle form submission from modal
        return redirect(url_for('attendance'))
    db = get_db_connection()
    cursor = db.cursor()

    if admin:
        cursor.execute(
            "SELECT attendance.id, student.student_name, attendance.date, attendance.status, attendance.student_id FROM attendance JOIN student ON student.id = attendance.student_id")
        attendance_data = cursor.fetchall()

        # For dropdown
        cursor.execute("SELECT id, student_id FROM student")
        student_data = cursor.fetchall()
    else:
        student_id = session.get('student_id')
        cursor.execute(
            "SELECT id, student_id FROM student WHERE student_id = %s", 
            (student_id,))
        student_data = cursor.fetchone()
        cursor.execute("SELECT * FROM attendance WHERE student_id = %s", (student_data[0],))
        attendance_data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('attendance.html', attendance=attendance_data, student=student_data)

# Record student attendance in the database
@app.route('/attendance/add', methods=['POST']) 
def add_attendance():
    if request.method == 'POST':
        # Get form data
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
            (student_id, date, status))
        db.commit()
        cursor.close()
        db.close()
        flash('Attendance record successfully added!', 'success')
    return redirect(url_for('attendance'))

# Update attendance data in the database
@app.route('/attendance/edit/<int:id>', methods=['POST'])
def edit_attendance(id):
    # Get form data
    student_id = request.form['student_id']
    date = request.form['date']
    status = request.form['status']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE attendance SET student_id=%s, date=%s, status=%s WHERE id=%s",
        (student_id, date, status, id))
    db.commit()
    cursor.close()
    db.close()
    flash('Attendance record successfully updated!', 'success')
    return redirect(url_for('attendance'))

# Delete attendance
@app.route('/attendance/delete/<int:id>')
def delete_attendance(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM attendance WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Attendance record successfully deleted!', 'success')
    return redirect(url_for('attendance'))

# Generate Attendance Report
@app.route('/attendance/report') 
def generate_attReport():
    pass
    
# Assessment Management
# Displaying assessment list
@app.route('/assessment')
def assessment():
    disable = {}
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM assessment")
    data = cursor.fetchall()
    admin = authorize()
    if admin:
        cursor.execute("SELECT * FROM student")
        student_data = cursor.fetchall()
    else: 
        student = session.get('student_id')
        cursor.execute("SELECT id, student_id FROM student WHERE student_id=%s",(student,))
        student_data = cursor.fetchone()
        for row in data: 
            assessment_id = row[0]
            cursor.execute(
                "SELECT COUNT(*) FROM assessment_response WHERE assessment_id=%s AND student_id=%s",
                (row[0], student_data[0]))
            response = cursor.fetchone()
            disable[assessment_id] = response[0] > 0
    cursor.close()
    db.close()
    return render_template('assessment.html', data=data, disable=disable, student=student_data)

# Render add assessment page
@app.route('/assessment/create')
def create_assessment():
    return render_template('add_assessment.html')

# Handle assessment creation
# Store assessment data (details, items, and choices) 
@app.route('/assessment/add', methods=['POST'])
def add_questionBank():
    db = get_db_connection()
    cursor = db.cursor()

    # Getting form request data
    form_data = request.form

    # Store assessment info in the database and get its id
    assessment_id = insert_assessment(cursor, form_data['assessment_type'], form_data['title'])

    # Process and store items in the database and get the ids
    item_ids, indexes = process_items(cursor, assessment_id, form_data)

    # Store choices in the database
    for index in indexes:
        choices = process_choices(item_ids[index], index, form_data)
        choice_sql = 'INSERT INTO assessment_choices (choice, item_id) VALUES (%s, %s)'
        cursor.executemany(choice_sql, choices)

    db.commit()
    cursor.close()
    db.close()
    flash('Assessment successfully added!', 'success')
    return redirect(url_for('assessment'))

# Store assessment details in the database
def insert_assessment(cursor,assessment_type, title):
    cursor.execute("INSERT INTO assessment (type, title) VALUES (%s, %s)", (assessment_type, title))
    return cursor.lastrowid

# Process and stores assessment items
def process_items(cursor, assessment_id, form_data):
    item_ids = {}
    indexes = []
    for key in form_data:
        if key.startswith('question_'):
            index = key.split('_')[1]
            type = form_data.get(f'item_type_{index}')
            item = {
                'type': type,
                'question': form_data.get(f'question_{index}'),
                'answer': form_data.get(f'answer_{index}'),
                'assessment_id': assessment_id
            }        
            item_id = insert_item(cursor, item)
            item_ids[index] = item_id
            if(type == 'Multiple Choice'):
                indexes.append(index)
    return item_ids, indexes

# Store the item data in the database
def insert_item(cursor, item):
    type = item['type']
    question = item['question']
    answer = item['answer']
    assessment_id = item['assessment_id']
    cursor.execute("INSERT INTO assessment_item (type, question, answer, assessment_id) VALUES (%s, %s, %s, %s)", (type, question, answer, assessment_id))
    return cursor.lastrowid

# Process item choices
def process_choices(item_id, index, form_data):
    choices = []
    raw_input = form_data[f'choices_{index}']
    raw_choices = raw_input.split(',')
    for c in raw_choices:
        choice = (c.strip(), item_id)        
        choices.append(choice)
    return choices

# Display assessment data and store assessment response
@app.route('/assessment/<int:id>/take', methods=['GET', 'POST'])
def take_assessment(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Storing assessment response
    if request.method == "POST":
        # Get student data
        student_id = request.form['student_id']
        cursor.execute(
                "SELECT id, student_id FROM student WHERE student_id = %s",
                (student_id,))
        student = cursor.fetchone()

        # Loop answers and store on database
        for key in request.form:
            if key.startswith('answer_'):
                # Get item data
                item_id = key.split('_')[1]
                cursor.execute("SELECT id, type, answer FROM assessment_item WHERE id = %s",(item_id,))
                type = cursor.fetchone()

                answer = request.form[f'answer_{item_id}']
                # Check assessment type
                if type[1] == 'Multiple Choice':
                    if type[2] == answer:
                        is_correct = True
                else:
                    is_correct = None 
                # Store each answer on the database
                cursor.execute(
                    "INSERT INTO assessment_response(answer, item_id, student_id, assessment_id, is_correct) VALUES (%s, %s, %s, %s, %s)",
                    (answer, item_id, student[0], id, is_correct))
                db.commit()
                cursor.close()
                db.close()
                flash("Assessment Completed!", 'success')
                return redirect(url_for('assessment'))
    
    # Group and aggregate items and choices
    items_query = "SELECT assessment_item.id, assessment_item.question, assessment_item.type, assessment_choices.choice, assessment_choices.item_id FROM assessment_item LEFT JOIN assessment_choices ON assessment_choices.item_id = assessment_item.id WHERE assessment_item.assessment_id = %s"
    df = pd.read_sql(items_query, db, params=(id,))
    grouped = df.groupby(['id', 'question', 'type'])['choice']\
                .apply(list).reset_index()
    items = grouped.to_dict(orient='records')

    # Get assessment data
    cursor.execute("SELECT * FROM assessment WHERE assessment.id = %s",(id,))
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template('take_assessment.html', assessment=data, items=items)

# Display assessment results
@app.route('/assessment/<int:assessment_id>/results/<int:student_id>')
def view_assessment(assessment_id, student_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Group and aggregate items and choices
    items_query = "SELECT assessment_item.id, assessment_item.question, assessment_item.answer, assessment_item.type, assessment_choices.choice, assessment_choices.item_id FROM assessment_item LEFT JOIN assessment_choices ON assessment_choices.item_id = assessment_item.id WHERE assessment_item.assessment_id = %s"
    df = pd.read_sql(items_query, db, params=(assessment_id,))
    grouped = df.groupby(['id', 'question', 'type', 'answer'])['choice']\
                .apply(list).reset_index()
    items = grouped.to_dict(orient='records')

    # Get assessment data
    cursor.execute("SELECT * FROM assessment WHERE assessment.id = %s",(assessment_id,))
    assessment = cursor.fetchone()

    # Get response data to compare with the correct answer
    cursor.execute("SELECT * FROM assessment_response WHERE assessment_id = %s and student_id=%s",(assessment_id, student_id))
    response = cursor.fetchall()

    # Get student data
    cursor.execute("SELECT id, year_section, student_id FROM student WHERE id = %s",(student_id,))
    student = cursor.fetchone()

    cursor.close()
    db.close()
    return render_template('view_assessment.html', assessment=assessment, items=items, student=student, response=response)

# Manual checking of answers
@app.route('/item/<int:id>/check', methods=['POST'])
def checkAnswer(id):
    # Handle ajax request
    data = request.get_json()
    status = data.get('status')
    student_id = data.get('student_id')

    db = get_db_connection()
    cursor = db.cursor()
    if status == 'correct':
        cursor.execute(
            "UPDATE assessment_response SET is_correct = %s WHERE item_id=%s AND student_id=%s",
            (True, id, student_id))
    else:
        cursor.execute(
            "UPDATE assessment_response SET is_correct = %s WHERE item_id=%s AND student_id=%s",
            (False, id, student_id))
    db.commit()
    cursor.close()
    db.close()

    # Return the JSON response
    return jsonify({
        'status': 'success',
    })

# Display assessment response
@app.route('/assessment/<int:id>/response')
def view_response(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Group response
    response_query = "SELECT assessment_response.id, assessment_response.is_correct, assessment_response.assessment_id, assessment_response.student_id, student.student_name  FROM assessment_response JOIN student ON student.id = assessment_response.student_id WHERE assessment_id = %s"
    df = pd.read_sql(response_query, db, params=(id,))
    grouped = df.groupby(['assessment_id','student_id', 'student_name'])['is_correct']\
                .apply(list).reset_index()

    # Add status to track response
    grouped['status'] = grouped['is_correct'].apply(
        lambda x: 'Unchecked' if any(pd.isna(i) for i in x) else 'Checked'
    )
    data = grouped.to_dict(orient='records')
    cursor.close()
    db.close()

    return render_template('response.html', data=data)

@app.route('/record/score', methods=['POST'])
def record_score():
    # Get form data
    score = request.form['score']
    student_id = request.form['student_id']
    assessment_id = request.form['assessment_id']
    date = request.form['date']
    
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO assessment_result (score, student_id, assessment_id, date) VALUES (%s, %s, %s, %s)',
        (score, student_id, assessment_id, date))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('assessment'))

# create admin account
def seed_user():
    db = get_db_connection()
    cursor = db.cursor()
    email = 'admin@gmail.com'
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        role = 'admin'
        password = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, password, role)
        )
        db.commit()
        cursor.close()
        db.close()
    

if __name__ == '__main__':
    seed_user()
    app.run(debug=True)
