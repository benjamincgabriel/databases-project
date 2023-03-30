import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func, text

from pypika import Query, Table, Field

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    if request.method == "POST":
        r = Table('room')
        query = Query.from_(r).select(r.roomid, r.tv, r.fridge, r.freezer, r.ac, r.isextendible, r.viewopt)

        tv = request.form.get('tv')
        if tv=="on":
            query = query.where(r.tv==True)

        fridge = request.form.get('fridge')
        if fridge=="on":
            query = query.where(r.fridge==True)
        
        freezer = request.form.get('freezer')
        if freezer=="on":
            query = query.where(r.freezer==True)
        
        ac = request.form.get('ac')
        if ac=="on":
            query = query.where(r.ac==True)

        isextendible = request.form.get('isextendible')
        if isextendible=="on":
            query = query.where(r.isextendible==True)
        
        view = request.form.get('view')
        if view=="mountain":
            query = query.where(r.viewopt=='Mountain')
        elif view=="sea":
            query = query.where(r.viewopt=='Sea')
        elif view=="river":
            query = query.where(r.viewopt=='River')
        elif view=="forest":
            query = query.where(r.viewopt=='Forest')

        rooms = db.session.execute(text(str(query))).mappings().all()

        return render_template("index.html", rooms=rooms, len=len(rooms))

    rooms = db.session.execute(text('select * from room')).mappings().all()
    return render_template("index.html", rooms=rooms, len=len(rooms))


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080)


