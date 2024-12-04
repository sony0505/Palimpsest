from flask import Flask, render_template

# Create a Flask app
app = Flask(__name__)
print("Flask app created")
# Define a route for the root URL
@app.route('/')
# Define a function to handle requests to the root URL
def index():
    #return "<h1>Hello, World!</h1>"
    return render_template('index.html')
@app.route('/user/<username>')

def user(username):
    #return "<h1>Hello {}</h1>".format(username)
    user_list = ['Alice', 'Bob', 'Charlie']
    return render_template('user.html', username=username, user_list=user_list)

# create a custom error page

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Invalid server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
