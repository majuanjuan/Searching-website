# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def init_db():
    """Creates the database."""
    with app.app_context():
       db = get_db()
       with app.open_resource('/var/www/html/flaskr/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
       db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db
    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
       top.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    with open('/var/www/html/flaskr/hardwarelist.txt') as fl:
          for eachline in fl:
             (model,sn,user,status)=eachline.strip().split(',')
             db.execute('insert into entries (model,sn,user,status) values (?, ?, ?, ?)',
                           (model,sn,user,status))
    fl.close()
    cur = db.execute('select model,sn,status,user from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/searchinguser', methods=['POST'])
def dosearchuser():
    db=get_db()
    douser=db.execute('select * from entries where user like ?',
                      [request.form['machine_users']])
    users = douser.fetchall()
    return render_template('searchinguser.html', users=users)

    
@app.route('/searchingstatus',methods=['POST'])
def dosearchstatus():
    db=get_db()
    dostatus=db.execute('select * from entries where status like ?',
                      [request.form['machine_status']])
    dsstatus = dostatus.fetchall()
    return render_template('searchingstatus.html', dsstatus=dsstatus)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (model,sn,status,user) values (?, ?, ?, ?)',
               [request.form['model'], request.form['sn'],request.form['status'],request.form['user']])
    db.commit()
    flash('Successfully added!')
    return redirect(url_for('show_entries'))

@app.route('/delete', methods=['POST'])
def remove_entry():
    if not session.get('logged_in'):
        abort(401)
    db=get_db()
    db.execute('delete from entries where sn like ?',
                      [request.form['rmsn']])
    db.commit()
    flash('Successfully deleted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

init_db()
