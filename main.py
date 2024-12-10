from flask import Flask, render_template,request, redirect, url_for, flash, session
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms.widgets import TextArea
from flask_migrate import Migrate
from functools import wraps
# Create a Flask app
app = Flask(__name__)
print("Flask app created")

# Create a secret key
app.config['SECRET_KEY'] = 'mysecretkey'
# Create a database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
# Create a database
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

# Create a model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    def __repr__(self): # This is a method that returns a string representation of the object, it is used to print the readable version of the object to us when debugging
        return '<UserName %r, UserEmail %r, UserID %r>' % (self.username, self.email, self.id)

class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True) # When using primary, it means that it is unique and generates automatically
    title = db.Column(db.String(20), nullable=False)
    diary = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self): # This is a method that returns a string representation of the object, it is used to print the readable version of the object to us when debugging
        return '<DiaryId %r, DiaryTitle %r, DiaryContent %r, DiaryDate %r, UserID %r>' % (self.id, self.title, self.diary, self.date, self.user_id)
# Create a form
class DiaryForm(FlaskForm):
    # python wtf field
    title = StringField('Title')
    diary = StringField('Write something', validators=[DataRequired()])
    #user_id = StringField('User ID(Debug only)')
    submit = SubmitField('Save')
class UserUpdateForm(FlaskForm):# I don't know how to change the button text, so I create a new form for update. I don't know if it is a good way to do it, I will learn it later
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Update')

class DiaryUpdateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    diary = StringField('Diary', validators=[DataRequired()])
    submit = SubmitField('Update')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('SignUp')

class LogInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Login')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('please_login'))
        return f(*args, **kwargs)
    return decorated_function

# Define a route for the root URL
@app.route('/')
# Define a function to handle requests to the root URL
def index():
    #return "<h1>Hello, World!</h1>"
    return render_template('index.html')

@app.route('/profile/<username>')
@login_required
def profile(username):
    return render_template('profile.html')

@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    diary_content = None
    form = DiaryForm()
    if form.validate_on_submit():
        diary_content = form.diary.data
        diary_title = form.title.data
        diary = Diary.query.filter_by(title=diary_title).first()
        if diary is None:
            diary = Diary(title=diary_title, diary=diary_content, user_id=session['user_id'])
            db.session.add(diary)
            db.session.commit()
        all_diary = Diary.query.filter_by(user_id=session['user_id']).order_by(Diary.id).all()
        return render_template('diary_warehouse.html', all_diary=all_diary)
    return render_template('write.html', form=form)

@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        user = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first() # Check if the email is already in the database. Need to check here, otherwise add the same email to the database will get system error
        
        if user is None and email_check is None:
            user = User(username=username, password=form.password.data, email=email)
            db.session.add(user)
            db.session.commit()
        # email already exists error message
        elif email_check:
            all_user = User.query.order_by(User.id).all()
            return render_template('SignUp.html', form=form, email_error="Email already exists", all_user=all_user)
    
    all_user = User.query.order_by(User.id).all()
    return render_template('SignUp.html', form=form, username=username, all_user=all_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = None
    form = LogInForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user is not None:
            if form.password.data == user.password:
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = user.id
                session['email'] = user.email
                return redirect(url_for('index'))
            else:
                return render_template('login.html', form=form, password_error="Invalid password")
        else:
            return render_template('login.html', form=form, username_error="Invalid username")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/user_update/<int:id>', methods=['GET', 'POST'])
def user_update(id):
    form = UserUpdateForm()
    user_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form['email']
        email_check = User.query.filter_by(email=email).first()
        
        if email_check and email_check.id != user_to_update.id:
            return render_template('user_update.html', form=form, user_to_update=user_to_update, 
                                email_error="Email already exists")
        
        try:
            user_to_update.username = request.form['username']
            user_to_update.password = request.form['password']
            user_to_update.email = email
            db.session.commit()
            return redirect(url_for('profile', username=session['username']))
        except:
            return render_template('user_update.html', form=form, user_to_update=user_to_update)
            
    return render_template('user_update.html', form=form, user_to_update=user_to_update)

@app.route('/diary_update/<int:id>', methods=['GET', 'POST'])
def diary_update(id):
    form = DiaryUpdateForm()
    diary_to_update = Diary.query.get_or_404(id)
    return render_template('diary_warehouse.html', form=form, diary_to_update=diary_to_update)

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = User.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('SignUp'))
    except:
        return redirect(url_for('SignUp'))

@app.route('/diary_warehouse')
@login_required
def diary_warehouse():
    # Get the diaries of the current user( Current user's diary only, later I will write a function to get the diary that the user has the authority to read base on the friend list. I will do it after I finish the friend relationship)
    user_diaries = Diary.query.filter_by(user_id=session['user_id']).order_by(Diary.date.desc()).all()
    return render_template('diary_warehouse.html', all_diary=user_diaries)

# create a custom error page
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Invalid server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()

# Run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
