from flask import Flask, render_template

# Create a Flask app
app = Flask(__name__)
print("Flask app created")
# Define a route for the root URL
@app.route('/')
# Define a function to handle requests to the root URL
def index():
    return "<h1>Hello, World!</h1>"
@app.route('/user/<username>')

def user(username):
    return "<h1>Hello {}</h1>".format(username)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
