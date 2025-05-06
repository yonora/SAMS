# Sley - Student Assessment and Management System

A Flask-based web application for managing student accounts, recording attendance and assessment scores, and generating reports.

## Features

## 🚀 Features

- Manage student accounts and information  
- Track and record student attendance  
- Create quizzes and exams, and record scores  
- Generate performance and attendance reports (PDF)

## Prerequisites

- Python 3.7+
- MySQL Database
- Git (for cloning the repository)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Sley.git
   cd Sley
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## MySQL Installation and Setup

### Windows
1. Download and install MySQL from the [official website](https://dev.mysql.com/downloads/installer/)
2. During installation, set a root password and remember it
3. Launch MySQL Command Line Client:
   ```
   mysql -u root -p
   ```
4. Enter your password when prompted

### macOS
1. Install MySQL using Homebrew:
   ```
   brew install mysql
   ```
2. Start MySQL service:
   ```
   brew services start mysql
   ```
3. Secure your MySQL installation:
   ```
   mysql_secure_installation
   ```
4. Connect to MySQL:
   ```
   mysql -u root -p
   ```

### Linux (Ubuntu/Debian)
1. Install MySQL:
   ```
   sudo apt update
   sudo apt install mysql-server
   ```
2. Secure your MySQL installation:
   ```
   sudo mysql_secure_installation
   ```
3. Connect to MySQL:
   ```
   sudo mysql
   ```
   or if you set a password:
   ```
   mysql -u root -p
   ```

## Database Setup

1. Create a MySQL database for the application:
   ```sql
   CREATE DATABASE sley_db;
   ```

2. Use the following SQL to create the required tables:
   ```sql
   USE sley_db;

   CREATE TABLE users (
     id INT AUTO_INCREMENT PRIMARY KEY,
     email VARCHAR(255) NOT NULL,
     password VARCHAR(255) NOT NULL,
     role VARCHAR(20) NOT NULL
   );

   CREATE TABLE student (
     id INT AUTO_INCREMENT PRIMARY KEY,
     student_id VARCHAR(10) NOT NULL,
     student_name VARCHAR(255) NOT NULL,
     year_section VARCHAR(255) NOT NULL
   );
   
   CREATE TABLE attendance (
     id INT AUTO_INCREMENT PRIMARY KEY,
     date DATE NOT NULL,
     status VARCHAR(50) NOT NULL,
     student_id INT NOT NULL,
     FOREIGN KEY (student_id) REFERENCES student(id)
   );
   

   CREATE TABLE assessment(
      id INT AUTO_INCREMENT PRIMARY KEY,
      type VARCHAR(20) NOT NULL,
      title VARCHAR(255) NOT NULL
   );

   CREATE TABLE assessment_item (
      id INT AUTO_INCREMENT PRIMARY KEY,
      type VARCHAR(50) NOT NULL,
      question TEXT NOT NULL,
      answer VARCHAR(255) NOT NULL,
      assessment_id INT NOT NULL,
      FOREIGN KEY (assessment_id) REFERENCES assessment(id)
   );

   CREATE TABLE assessment_choices (
      id INT AUTO_INCREMENT PRIMARY KEY,
      choice VARCHAR(50) NOT NULL,
      item_id INT NOT NULL,
      FOREIGN KEY (item_id) REFERENCES assessment_item(id)
   );

   CREATE TABLE assessment_response (
      id INT AUTO_INCREMENT PRIMARY KEY,
      answer VARCHAR(255) NOT NULL,
      item_id INT NOT NULL,
      FOREIGN KEY(item_id) REFERENCES assessment_item(id),
      student_id INT NOT NULL,
      FOREIGN KEY (student_id) REFERENCES student(id),
      assessment_id INT NOT NULL,
      FOREIGN KEY(assessment_id) REFERENCES assessment(id),
      is_correct BOOLEAN
   );

   CREATE TABLE assessment_result (
      id INT AUTO_INCREMENT PRIMARY KEY,
      score INT NOT NULL,
      student_id INT NOT NULL,
      FOREIGN KEY (student_id) REFERENCES student(id),
      assessment_id INT NOT NULL,
      FOREIGN KEY (assessment_id) REFERENCES assessment(id),
      date DATE NOT NULL
   );
   
   ```

## Environment Configuration

1. Create a `.env` file in the project root directory:
   ```
   DB_HOST=localhost
   DB_USER=your_database_username
   DB_PASSWORD=your_database_password
   DB_NAME=sley_db
   SECRET_KEY=your_secret_key_here
   ```

   Replace the values with your actual database credentials and create a secure random string for SECRET_KEY.

## Running the Application

1. Start the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Project Structure

- `app.py` - The main Flask application
- `templates/` - HTML templates
  - `index.html` - Home page
  - `attendance.html` - Attendance management
  - `base.html` - Base template for authenticated users
  - `guest.html` - Base template for guest
  - `login.html` - Admin login page
  - `student_login.html` - Student login page
  - `student_info.html` - Student account/info management
  - `assessment.html` - Assessment management
  - `add_assessment.html` - Question bank creation
  - `assessment_module.html` - Quiz and Exam Module
  - `assessment_results.html` - Assessment results page
  - `response.html` - Assessment response page
- `static/js` - Static files
  - `alert.js` - JavaScript for displaying alerts and notifications

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
