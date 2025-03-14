# Sley - Student Management System

A Flask-based web application for managing student attendance, exams, and quizzes.

## Features

- Track student attendance
- Manage exam records
- Record quiz results
- Simple and intuitive interface

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

   #### After cloning the repo, extract the zip file and then navigate to the directory
   ```
   cd tracker
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
   
   CREATE TABLE attendance (
     id INT AUTO_INCREMENT PRIMARY KEY,
     student_name VARCHAR(255) NOT NULL,
     date DATE NOT NULL,
     status VARCHAR(50) NOT NULL
   );
   
   CREATE TABLE exam (
     id INT AUTO_INCREMENT PRIMARY KEY,
     student_name VARCHAR(255) NOT NULL,
     exam_date DATE NOT NULL,
     score FLOAT NOT NULL
   );
   
   CREATE TABLE quiz (
     id INT AUTO_INCREMENT PRIMARY KEY,
     student_name VARCHAR(255) NOT NULL,
     quiz_date DATE NOT NULL,
     score FLOAT NOT NULL
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
  - `exam.html` - Exam records
  - `quiz.html` - Quiz results
  - `base.html` - Base template for consistent layout
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
