import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from multiprocessing import Value
import logging,platform,sys

from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(levelname)s]:[%(name)s]:[%(asctime)s] %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask("Techtrends")
app.config['SECRET_KEY'] = 'everythingIsFine'
db_connection_count = 0
post_count = 0

@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    global post_count
    if post_count == 0:
        post_count = len(posts)
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error("- %s - Article with id %s doesn't exist",request.host)
      return render_template('404.html'), 404
    else:
      global db_connection_count
      db_connection_count += 1
      app.logger.info("- %s - An article is retrieved - %s",request.host, post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("- %s - The ""About Us"" page is retrieved",request.host)
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            global post_count
            post_count += 1
            app.logger.info("- %s - A new article is posted - %s", request.host, title)
            app.logger.debug("- %s - Current number of posts - %s", request.host, post_count)
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health check endpoint
@app.route('/healthz')
def healthz():
    data = { 
            "result" : "OK - healthy", 
        } 
    return jsonify(data), 200

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    global db_connection_count
    global post_count
    data = { 
            "db_connection_count": db_connection_count,
            "post_count": post_count, 
        } 
    app.logger.debug("- %s - Metrics - { db_connection_count - %s & post_count - %s }",request.host, data["db_connection_count"], data["post_count"])
    return jsonify(data), 200

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
