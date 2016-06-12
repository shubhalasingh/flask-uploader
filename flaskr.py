import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory,g,flash
from datetime import datetime 
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/path/to/the/uploads'
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER='upload'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    # Initializes the database
    init_db()
    print 'Initialized the database.'

@app.route('/list')
def show_entries():
    db = get_db()
    cur = db.execute('select title,datetime from entries order by datetime desc')
    entries = cur.fetchall()
    # return render_template('up.html', entries=entries)
    return render_template('list_up.html', entries=entries)
    

def add_entry(filename):
    db = get_db()
    db.execute('insert into entries (title, datetime) values (?, ?)',
                 [filename, datetime.now()])
    db.commit()
    flash('New file is successfully posted')

@app.route('/',methods=['GET','POST'])        
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        else:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # save in DB
                add_entry(filename)
                return redirect(url_for('show_entries'))
    else:
        return render_template('up.html') 

@app.route('/uploads/<filename>',methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

	



