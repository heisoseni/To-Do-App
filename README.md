Todo App with Authentication

A clean and secure personal Todo application built with **Flask**, **Flask-Login**, **SQLAlchemy**, and **Tailwind CSS**.

Live Demo: (https://to-do-app-95wp.onrender.com)

Features
- User Registration & Login
- Secure password hashing
- Remember me functionality
- Change password
- Create, complete, and delete tasks
- Each user only sees their own tasks
- Modern dark UI with Tailwind CSS

Technologies Used
- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Werkzeug (password hashing)
- Tailwind CSS
- SQLite
- Gunicorn (for production)

What I Learned
- Implementing user authentication with Flask-Login
- Password hashing and security best practices
- Creating relationships between models (User ↔ Task)
- Protecting routes with `@login_required`
- Building a clean and modern UI with Tailwind
- Deploying a Flask application

How to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/heisoseni/To-Do-App.git
   cd To-Do-App
   
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate   # Mac/Linux

3. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Run the app:
   ```bash
   python app.py

5. Open your browser at: http://127.0.0.1:5000


Project Structure
- Full authentication system
- User-specific tasks
- Clean and responsive dark interface
