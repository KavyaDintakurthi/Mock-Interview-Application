import os
import json
import logging
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "mock-interview-app-secret")
app.config['SESSION_TYPE'] = 'filesystem'

# Load questions data
def load_questions():
    try:
        with open('static/data/questions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Questions file not found, creating empty questions data")
        return {"technical": {}, "behavioral": {}, "domain": {}}

# Load job roles data
def load_jobs():
    try:
        with open('static/data/jobs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Jobs file not found, creating empty jobs data")
        return []

# In-memory user storage (would be replaced with database in production)
users = {}
# In-memory interview results storage
interview_results = {}

# Store questions data in memory (load from JSON file)
questions_data = load_questions()
jobs_data = load_jobs()

# Routes
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and users[email]['password'] == password:
            session['user'] = {
                'email': email,
                'name': users[email]['name']
            }
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users:
            flash('Email already exists. Please use a different email.', 'danger')
        else:
            users[email] = {
                'name': name,
                'email': email,
                'password': password,  # In a real app, hash this password
                'resume': '',
                'preferences': {},
                'skills': []
            }
            session['user'] = {
                'email': email,
                'name': name
            }
            flash('Registration successful!', 'success')
            return redirect(url_for('profile'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        flash('Please login to access your profile.', 'warning')
        return redirect(url_for('login'))
    
    user_email = session['user']['email']
    user_data = users.get(user_email, {})
    
    if request.method == 'POST':
        # Update profile information
        user_data['name'] = request.form.get('name')
        user_data['resume'] = request.form.get('resume')
        user_data['skills'] = request.form.get('skills').split(',')
        users[user_email] = user_data
        session['user']['name'] = user_data['name']
        flash('Profile updated successfully!', 'success')
    
    return render_template('profile.html', user=user_data)

@app.route('/configure', methods=['GET', 'POST'])
def configure_interview():
    if 'user' not in session:
        flash('Please login to configure an interview.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Store interview configuration in session
        session['interview_config'] = {
            'job_role': request.form.get('job_role'),
            'interview_type': request.form.get('interview_type'),
            'difficulty': request.form.get('difficulty'),
            'duration': int(request.form.get('duration')),
            'timestamp': int(time.time())
        }
        
        # Generate questions based on configuration
        interview_type = request.form.get('interview_type')
        difficulty = request.form.get('difficulty')
        job_role = request.form.get('job_role')
        
        # Select questions from our data store based on interview type and difficulty
        selected_questions = []
        
        if interview_type in questions_data and job_role in questions_data[interview_type]:
            all_questions = questions_data[interview_type][job_role].get(difficulty, [])
            
            # If we don't have enough questions for the specific difficulty, include questions from all difficulties
            if len(all_questions) < 5:
                all_questions = []
                for diff in ['easy', 'medium', 'hard']:
                    all_questions.extend(questions_data[interview_type][job_role].get(diff, []))
            
            # Randomly select 5 questions or all if less than 5 are available
            selected_questions = random.sample(all_questions, min(5, len(all_questions)))
        
        # If we still don't have enough questions, add some default questions
        if len(selected_questions) < 5:
            default_questions = [
                "Tell me about yourself and your experience.",
                "What are your strengths and weaknesses?",
                "Why do you want to work in this role?",
                "Describe a challenging project you worked on.",
                "Where do you see yourself in 5 years?"
            ]
            # Add as many default questions as needed to reach 5
            selected_questions.extend(default_questions[:(5-len(selected_questions))])
        
        # Store selected questions in session
        session['interview_questions'] = selected_questions
        return redirect(url_for('interview'))
    
    return render_template('configure.html', jobs=jobs_data)

@app.route('/interview')
def interview():
    if 'user' not in session:
        flash('Please login to start an interview.', 'warning')
        return redirect(url_for('login'))
    
    if 'interview_config' not in session or 'interview_questions' not in session:
        flash('Please configure your interview first.', 'warning')
        return redirect(url_for('configure_interview'))
    
    config = session['interview_config']
    questions = session['interview_questions']
    
    return render_template('interview.html', config=config, questions=questions)

@app.route('/submit_interview', methods=['POST'])
def submit_interview():
    if 'user' not in session:
        flash('Please login to submit an interview.', 'warning')
        return redirect(url_for('login'))
    
    # Get the answers from the form
    answers = {}
    for i, question in enumerate(session.get('interview_questions', [])):
        answers[question] = request.form.get(f'answer_{i}', '')
    
    # Calculate a mock score (in a real application, this would be more sophisticated)
    score = 0
    feedback = {}
    
    for question, answer in answers.items():
        # Simple scoring based on answer length
        if len(answer) > 200:
            q_score = random.randint(80, 100)
        elif len(answer) > 100:
            q_score = random.randint(60, 80)
        elif len(answer) > 50:
            q_score = random.randint(40, 60)
        else:
            q_score = random.randint(20, 40)
        
        score += q_score
        
        # Generate mock feedback
        if q_score >= 80:
            fb = "Excellent answer! Very comprehensive and well-articulated."
        elif q_score >= 60:
            fb = "Good answer. You covered the important points but could add more detail."
        elif q_score >= 40:
            fb = "Adequate answer but lacks depth. Consider providing examples."
        else:
            fb = "This answer needs improvement. Try to be more specific and detailed."
        
        feedback[question] = {
            'score': q_score,
            'feedback': fb
        }
    
    # Calculate average score
    avg_score = score / len(answers) if answers else 0
    
    # Store the result
    result_id = str(int(time.time()))
    interview_results[result_id] = {
        'user_email': session['user']['email'],
        'config': session.get('interview_config', {}),
        'questions': session.get('interview_questions', []),
        'answers': answers,
        'feedback': feedback,
        'score': avg_score,
        'timestamp': int(time.time())
    }
    
    # Store result_id in session
    session['last_result_id'] = result_id
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    if 'user' not in session:
        flash('Please login to view results.', 'warning')
        return redirect(url_for('login'))
    
    result_id = session.get('last_result_id')
    if not result_id or result_id not in interview_results:
        flash('No interview results found.', 'warning')
        return redirect(url_for('configure_interview'))
    
    result = interview_results[result_id]
    
    return render_template('results.html', result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
