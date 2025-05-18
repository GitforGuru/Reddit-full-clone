from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from model import db, User

app = Flask(__name__)
# Configure database - replace with your actual MySQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://GURITO:GURITO@localhost/signit_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key

# Initialize the database with this app
db.init_app(app)

# Create all tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        dob= request.form['dob']
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        # Create new user
        new_user = User(
            username=username,
            email=email,
            dob=dob,
            password_hash=generate_password_hash(password),
            created_at=datetime.utcnow()

        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user.password_hash, password):
            # Store user info in session
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access the dashboard')
        return redirect(url_for('login'))
        
    # Get user data
    user = User.query.get(session['user_id'])
    
    return render_template('dashboard.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
