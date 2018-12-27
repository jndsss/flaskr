import os
import sqlite3
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash

app = Flask(__name__) # Create instance
app.config.from_object(__name__) # load config from flaskr.py

app.config.update(
    dict(
        DATABASE = os.path.join(app.root_path,'flaskr.db'),
        SECRET_KEY = 'development key',
        USERNAME = 'admin',
        PASSWORD = 'default'
    )
)
app.config.from_envvar('FLASKR_SETTINGS',silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """ opens a new connection if there is none yet for current app context"""
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db =  connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """ close the database again at the end of the request"""
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/")
def show_entries():
    db = get_db()
    cur = db.execute("select title, text from entries order by id desc")
    entries =  cur.fetchall()
    return render_template("show_entries.html", entries = entries)

@app.route("/add", methods = ["POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)
    db = get_db()
    db.execute("insert into entries (title, text) values(?,?)",[request.form['title'], request.form['text']])
    db.commit()
    flash("new entry was posted")
    return redirect(url_for("show_entries"))


@app.route("/login", methods = ["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error = 'Invalid username'
        elif request.form["password"] != app.config["PASSWORD"]:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash("you are logged in")
            return redirect(url_for("show_entries"))
    return render_template("login.html", error = error)

@app.route("/logout")
def logout():
    session.pop('logged_in',None)
    flash('you are logged out')
    return redirect(url_for("show_entries"))

if __name__ == '__main__':
    app.run()

