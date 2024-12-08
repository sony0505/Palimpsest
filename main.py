from flask import Flask, render_template,request, redirect, url_for, flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Create a Flask app
app = Flask(__name__)
print("Flask app created")

# Create a secret key
app.config['SECRET_KEY'] = 'mysecretkey'
# Create a database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
# Create a database
db = SQLAlchemy(app)

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
    diary = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self): # This is a method that returns a string representation of the object, it is used to print the readable version of the object to us when debugging
        return '<DiaryId %r>' % self.id
# Create a form
class DiaryForm(FlaskForm):
    # python wtf field
    diary = StringField('Write something', validators=[DataRequired()])
    submit = SubmitField('Save')
class UpdateForm(FlaskForm):# I don't know how to change the button text, so I create a new form for update. I don't know if it is a good way to do it, I will learn it later
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
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

# Define a route for the root URL
@app.route('/')
# Define a function to handle requests to the root URL
def index():
    #return "<h1>Hello, World!</h1>"
    return render_template('index.html')

@app.route('/user/<username>')
def user(username):
    #return "<h1>Hello {}</h1>".format(username)
    user_list = ['Alice', 'Bob', 'Charlie'] # Get from database after database is created
    return render_template('user.html', username=username, user_list=user_list)

@app.route('/write', methods=['GET', 'POST'])
def write():
    diary_content = None
    form = DiaryForm()
    if form.validate_on_submit():
        diary_content = form.diary.data
        return render_template('write.html', diary=diary_content, date=datetime.now().strftime('%Y-%m-%d'))
    return render_template('write.html', diary=diary_content,form=form) # Even if the user doesn't submit the form, the diary_content still need to be transferred to the write.html,because detect whether duary is empty to show different html

@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first() # Check if the username is already in the database. If it is, it will return the user object, if not, it will return None
        if user is None: # If the username is not in the database, create a new user, else, it is already in the database, so don't add again
            user = User(username=username, password=form.password.data, email=form.email.data)
            print(user.username, user.password, user.email)
            db.session.add(user)
            db.session.commit()
        # Else print error message use flash, I will learn it later
    all_user = User.query.order_by(User.id).all() # Get all the users from the database and order them by id
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
                return render_template('login.html', form=form, username=username)
            else:
                return render_template('login.html', form=form, username=username, password_error="Invalid password")
        else:
            return render_template('login.html', form=form, username=username, username_error="Invalid username")
    return render_template('login.html', form=form, username=username)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UpdateForm()
    user_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.username = request.form['username']
        user_to_update.password = request.form['password']
        user_to_update.email = request.form['email']
        try:
            db.session.commit()
            return redirect(url_for('SignUp'))
        except:
            return render_template('update.html', form=form, user_to_update=user_to_update)
    return render_template('update.html', form=form, user_to_update=user_to_update)

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = User.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('SignUp'))
    except:
        return redirect(url_for('SignUp'))
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
    with app.app_context():# This is used to create a context for the database, make sure the database is created in the correct context(environment)
        #db.drop_all()     # remove all tables
        db.create_all()   # If there is no table, create a new one and add the models to it
        # db operations can't be executed outside the context, have to be inside the context(make sure the database is created in the correct environment)

# Run the app
if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
