from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return redirect(url_for('check', action='signin'))

@app.route('/check', methods=['GET', 'POST'])
def check():
    action = request.args.get('action', 'signin')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if action == 'signin':
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash("Sign In Successful!")
                return redirect(url_for('home'))
            else:
                flash("Invalid Credentials, Please Try Again.")
        
        elif action == 'signup':
            name = request.form.get('name')
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please log in.")
                return redirect(url_for('check', action='signin'))
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(name=name, email=email, password=hashed_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("User Registered Successfully!")  
                return redirect(url_for('check', action='signin'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}")
                return redirect(url_for('check', action='signup'))
    
    return render_template('check.html', action=action)

@app.route('/display_video')
def display_video():
    # Assuming `video_path` is the path to the uploaded video
    video_path = 'path/to/video.mp4'  # Adjust this based on your setup
    return render_template('display_video.html', video_path=video_path)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)
    else:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('check', action='signin'))
                                    
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('check', action='signin'))

@app.route('/home')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('home.html', user=user)
    flash("Please log in to access the dashboard.")
    return redirect(url_for('check', action='signin'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    flash("Please log in to access your profile.")
    return redirect(url_for('check', action='signin'))

@app.route('/settings')
def settings():
    if 'user_id' in session:
        return render_template('settings.html')
    flash("Please log in to access settings.")
    return redirect(url_for('check', action='signin'))

@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return {'user': user}
    return {'user': None}

from flask import Flask, render_template, redirect, url_for, request, session, flash
import os

@app.route('/sync', methods=['POST'])
def sync():
    if 'user_id' in session:
        video = request.files.get('video')
        audio = request.files.get('audio')
        
        if not video or not audio:
            flash("Please upload both video and audio files.")
            return redirect(url_for('home'))
        
        # Save files to the server (you can define a directory for uploads)
        video_path = os.path.join('uploads', video.filename)
        audio_path = os.path.join('uploads', audio.filename)

        video.save(video_path)
        audio.save(audio_path)

        # Syncing logic (Placeholder)
        flash("Video and audio files uploaded and synced successfully!")
        return redirect(url_for('home'))

    flash("Please log in to sync files.")
    return redirect(url_for('check', action='signin'))


if __name__ == '__main__':
    # Create database tables if they don't exist
    if not os.path.exists("users.db"):
        with app.app_context():
            db.create_all()
            print("Database created successfully!")
    app.run(debug=True)
