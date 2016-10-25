# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key', 
    USERNAME='admin',
    PASSWORD='default' 
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    with open('hardwarelist.txt') as fl:
        for eachline in fl:
           (model,sn,user,status)=eachline.strip().split(',')
           db.execute('insert into entries (model,sn,user,status) values (?, ?, ?, ?)',
                          (model,sn,user,status))
    fl.close()
    db.commit()
    

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


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


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select model,sn,status,user from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/searchinguser', methods=['POST'])
def dosearchuser():
    db=get_db()
    douser=db.execute('select * from entries where user like ?',
                      [request.form['machine_users']])
    users = douser.fetchall()
    print users
    return render_template('searchinguser.html', users=users)

    
@app.route('/searchingstatus',methods=['POST'])
def dosearchstatus():
    db=get_db()
    dostatus=db.execute('select * from entries where status like ?',
                      [request.form['machine_status']])
    dsstatus = dostatus.fetchall()
    print dsstatus
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
