import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func, text
from sqlalchemy import Delete, Update, Insert

from pypika import (
    AliasedQuery,
    Case,
    ClickHouseQuery,
    EmptyCriterion,
    Field,
    Index,
    MSSQLQuery,
    MySQLQuery,
    NullValue,
    OracleQuery,
    Order,
    PostgreSQLQuery,
    Query,
    QueryException,
    RedshiftQuery,
    SQLLiteQuery,
    Table,
    Tables,
    VerticaQuery,
    functions as fn,
    SYSTEM_TIME,
)
from pypika.terms import ValueWrapper

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    if request.method == "POST":
        r, has, hotel, owns, hotelchain = Table('room'), Table('has'), Table('hotel'), Table('owns'), Table('hotelchain')
        subquery = Query.from_(has).select(has.hotelid, fn.Count(has.roomid)).groupby(has.hotelid)

        query = Query.from_(r).join(has).on(r.roomid == has.roomid).join(hotel).on(has.hotelid == hotel.hotelid).join(owns).on(hotel.hotelid == owns.hotelid).join(hotelchain).on(owns.chainid == hotelchain.chainid).select(r.roomid, r.tv, r.fridge, r.freezer, r.ac, r.isextendible, r.viewopt, r.capacity, r.price, hotel.rating, hotelchain.chainname, hotel.address).join(subquery).on(subquery.hotelid == has.hotelid)

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
        

        capa = request.form.get('capacity')
        if capa!=None:
            cap = capa.split(', ')
            cap = [int(i) for i in cap]
            query = query.where(r.capacity >= cap[0])
            query = query.where(r.capacity <= cap[1])

        
        pri = request.form.get('price')
        if pri!=None:
            price = pri.split(', ')
            price = [int(i) for i in price]
            query = query.where(r.price >= price[0])
            query = query.where(r.price <= price[1])
        
        cnt = request.form.get('roomcount')
        if cnt!=None:
            count = cnt.split(', ')
            count = [int(i) for i in count]
            query = query.where(subquery.count >= count[0])
            query = query.where(subquery.count <= count[1])
        
        rating = request.form.get('category')
        if rating!="any":
            query = query.where(hotel.rating == int(rating))
        
        chain = request.form.get('hotelchain')
        if chain!="any":
            query = query.where(hotelchain.chainname == str(chain))
        
        address = request.form.get('area')
        if address!="any":
            query = query.where(hotel.address == str(address))

        rooms = db.session.execute(text(str(query))).mappings().all()

        hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
        hotels = db.session.execute(text('select * from hotel')).mappings().all()

        return render_template("index.html", rooms=rooms, len=len(rooms), hotelchains=hotelchains, numhotelchains=len(hotelchains), hotels=hotels, numhotels=len(hotels))

    hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
    hotels = db.session.execute(text('select * from hotel')).mappings().all()
    rooms = db.session.execute(text('select * from room')).mappings().all()
    return render_template("index.html", rooms=rooms, len=len(rooms), hotelchains=hotelchains, numhotelchains=len(hotelchains), hotels=hotels, numhotels=len(hotels))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    return render_template("admin.html")


@app.route("/deletehotelchain", methods=["GET", "POST"])
def deletehotelchain():
    if request.method == "POST":
        r, has, hotel, owns, hotelchain = Table('room'), Table('has'), Table('hotel'), Table('owns'), Table('hotelchain')
        hotelchaindelete = request.form.get('hotelchaindelete')

        if hotelchaindelete!="none":
            query = Query.from_(hotelchain).delete().where(hotelchain.chainname==hotelchaindelete)
            print(query)
            db.session.execute(text(str(query)))
            db.session.commit()

        hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
        return render_template("deletehotelchain.html", hotelchains=hotelchains, numhotelchains=len(hotelchains))
    
    hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
    return render_template("deletehotelchain.html", hotelchains=hotelchains, numhotelchains=len(hotelchains))


@app.route("/deletecustomer", methods=["GET", "POST"])
def deletecustomer():
    if request.method == "POST":
        customer = Table('customer')
        customerdelete = request.form.get('customerdelete')

        if customerdelete!="none":
            query = Query.from_(customer).delete().where(customer.customername==customerdelete)
            print(query)
            db.session.execute(text(str(query)))
            db.session.commit()

        customers = db.session.execute(text('select * from customer')).mappings().all()
        return render_template("deletecustomer.html", customers=customers, numcustomers=len(customers))
    
    customers = db.session.execute(text('select * from customer')).mappings().all()
    return render_template("deletecustomer.html", customers=customers, numcustomers=len(customers))


@app.route("/deleteemployee", methods=["GET", "POST"])
def deleteemployee():
    if request.method == "POST":
        employee = Table('employee')
        employeedelete = request.form.get('employeedelete')

        if employeedelete!="none":
            query = Query.from_(employee).delete().where(employee.employeename==employeedelete)
            print(query)
            db.session.execute(text(str(query)))
            db.session.commit()

        employees = db.session.execute(text('select * from employee')).mappings().all()
        return render_template("deleteemployee.html", employees=employees, numemployees=len(employees))
    
    employees = db.session.execute(text('select * from employee')).mappings().all()
    return render_template("deleteemployee.html", employees=employees, numemployees=len(employees))


@app.route("/deletehotel", methods=["GET", "POST"])
def deletehotel():
    if request.method == "POST":
        hotel = Table('hotel')
        hoteldelete = request.form.get('hoteldelete')

        if hoteldelete!="none":
            query = Query.from_(hotel).delete().where(hotel.hotelname==hoteldelete)
            print(query)
            db.session.execute(text(str(query)))
            db.session.commit()

        hotels = db.session.execute(text('select * from hotel')).mappings().all()
        return render_template("deletehotel.html", hotels=hotels, numhotels=len(hotels))
    
    hotels = db.session.execute(text('select * from hotel')).mappings().all()
    return render_template("deletehotel.html", hotels=hotels, numhotels=len(hotels))


@app.route("/deleteroom", methods=["GET", "POST"])
def deleteroom():
    if request.method == "POST":
        room = Table('room')
        roomdelete = request.form.get('roomdelete')

        if roomdelete!="none":
            query = Query.from_(room).delete().where(room.roomid==roomdelete)
            print(query)
            db.session.execute(text(str(query)))
            db.session.commit()

        rooms = db.session.execute(text('select * from room')).mappings().all()
        return render_template("deleteroom.html", rooms=rooms, numrooms=len(rooms))
    
    rooms = db.session.execute(text('select * from room')).mappings().all()
    return render_template("deleteroom.html", rooms=rooms, numrooms=len(rooms))


@app.route("/addcustomer", methods=["GET", "POST"])
def addcustomer():
    if request.method == "POST":
        customer = Table('customer')
        
        query = Query.into(customer).insert(request.form.get('ssn'), request.form.get('name'), request.form.get('address'), request.form.get('date'))
        print(query)
        db.session.execute(text(str(query)))
        db.session.commit()

        return render_template("addcustomer.html")
    
    return render_template("addcustomer.html")


@app.route("/addemployee", methods=["GET", "POST"])
def addemployee():
    if request.method == "POST":
        employee = Table('employee')
        
        query = Query.into(employee).insert(request.form.get('ssn'), request.form.get('name'), request.form.get('address'), request.form.get('role'))
        print(query)
        db.session.execute(text(str(query)))
        db.session.commit()

        return render_template("addemployee.html")
    
    return render_template("addemployee.html")


@app.route("/addhotel", methods=["GET", "POST"])
def addhotel():
    if request.method == "POST":
        hotel = Table('hotel')
        
        query = Query.into(hotel).insert(request.form.get('id'), request.form.get('name'), request.form.get('phonenumber'), request.form.get('contactemail'), int(request.form.get('rating')), request.form.get('address'))
        print(query)
        db.session.execute(text(str(query)))
        db.session.commit()

        return render_template("addhotel.html")
    
    return render_template("addhotel.html")


@app.route("/addroom", methods=["GET", "POST"])
def addroom():
    if request.method == "POST":
        room = Table('room')

        tv = request.form.get('tv')=="on"
        fridge = request.form.get('fridge')=="on"
        freezer = request.form.get('freezer')=="on"
        ac = request.form.get('ac')=="on"
        ext = request.form.get('ext')=="on"
        dmg = request.form.get('dmg')=="on"
        
        query = Query.into(room).insert(int(request.form.get('id')), ext, int(request.form.get('roomnumber')), int(request.form.get('price')), int(request.form.get('capacity')), ac, tv, fridge, freezer, dmg, str(request.form.get('view')))
        print(query)
        db.session.execute(text(str(query)))
        db.session.commit()

        return render_template("addroom.html")
    
    return render_template("addroom.html")


@app.route("/addbooking", methods=["GET", "POST"])
def addbooking():
    if request.method == "POST":
        booking = Table('booking')

        query = Query.into(booking).insert(int(request.form.get('id')), int(request.form.get('roomid')), int(request.form.get('hotelid')), int(request.form.get('ssn')), request.form.get('startdate'), request.form.get('enddate'), int(request.form.get('numberofguests')))
        print(query)
        db.session.execute(text(str(query)))
        db.session.commit()

        employees = db.session.execute(text('select * from employee')).mappings().all()
        hotels = db.session.execute(text('select * from hotel')).mappings().all()
        rooms = db.session.execute(text('select * from room')).mappings().all()
        return render_template("addbooking.html", rooms=rooms, numrooms=len(rooms), hotels=hotels, numhotels=len(hotels), employees=employees, numemployees=len(employees))

    employees = db.session.execute(text('select * from employee')).mappings().all()
    hotels = db.session.execute(text('select * from hotel')).mappings().all()
    rooms = db.session.execute(text('select * from room')).mappings().all()
    return render_template("addbooking.html", rooms=rooms, numrooms=len(rooms), hotels=hotels, numhotels=len(hotels), employees=employees, numemployees=len(employees))


@app.route("/budget", methods=["GET", "POST"])
def budget():
    if request.method == "POST":
        r, has, hotel, owns, hotelchain = Table('budget'), Table('has'), Table('hotel'), Table('owns'), Table('hotelchain')
        subquery = Query.from_(has).select(has.hotelid, fn.Count(has.roomid)).groupby(has.hotelid)

        query = Query.from_(r).join(has).on(r.roomid == has.roomid).join(hotel).on(has.hotelid == hotel.hotelid).join(owns).on(hotel.hotelid == owns.hotelid).join(hotelchain).on(owns.chainid == hotelchain.chainid).select(r.roomid, r.tv, r.fridge, r.freezer, r.ac, r.isextendible, r.viewopt, r.capacity, r.price, hotel.rating, hotelchain.chainname, hotel.address).join(subquery).on(subquery.hotelid == has.hotelid)

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
        

        capa = request.form.get('capacity')
        if capa!=None:
            cap = capa.split(', ')
            cap = [int(i) for i in cap]
            query = query.where(r.capacity >= cap[0])
            query = query.where(r.capacity <= cap[1])

        
        pri = request.form.get('price')
        if pri!=None:
            price = pri.split(', ')
            price = [int(i) for i in price]
            query = query.where(r.price >= price[0])
            query = query.where(r.price <= price[1])
        
        cnt = request.form.get('roomcount')
        if cnt!=None:
            count = cnt.split(', ')
            count = [int(i) for i in count]
            query = query.where(subquery.count >= count[0])
            query = query.where(subquery.count <= count[1])
        
        rating = request.form.get('category')
        if rating!="any":
            query = query.where(hotel.rating == int(rating))
        
        chain = request.form.get('hotelchain')
        if chain!="any":
            query = query.where(hotelchain.chainname == str(chain))
        
        address = request.form.get('area')
        if address!="any":
            query = query.where(hotel.address == str(address))

        rooms = db.session.execute(text(str(query))).mappings().all()

        hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
        hotels = db.session.execute(text('select * from hotel')).mappings().all()

        return render_template("index.html", rooms=rooms, len=len(rooms), hotelchains=hotelchains, numhotelchains=len(hotelchains), hotels=hotels, numhotels=len(hotels))

    hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
    hotels = db.session.execute(text('select * from hotel')).mappings().all()
    rooms = db.session.execute(text('select * from budget')).mappings().all()
    return render_template("index.html", rooms=rooms, len=len(rooms), hotelchains=hotelchains, numhotelchains=len(hotelchains), hotels=hotels, numhotels=len(hotels))


@app.route("/luxury", methods=["GET", "POST"])
def luxury():
    if request.method == "POST":
        r, has, hotel, owns, hotelchain = Table('luxury'), Table('has'), Table('hotel'), Table('owns'), Table('hotelchain')
        subquery = Query.from_(has).select(has.hotelid, fn.Count(has.roomid)).groupby(has.hotelid)

        query = Query.from_(r).join(has).on(r.roomid == has.roomid).join(hotel).on(has.hotelid == hotel.hotelid).join(owns).on(hotel.hotelid == owns.hotelid).join(hotelchain).on(owns.chainid == hotelchain.chainid).select(r.roomid, r.tv, r.fridge, r.freezer, r.ac, r.isextendible, r.viewopt, r.capacity, r.price, hotel.rating, hotelchain.chainname, hotel.address).join(subquery).on(subquery.hotelid == has.hotelid)

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
        

        capa = request.form.get('capacity')
        if capa!=None:
            cap = capa.split(', ')
            cap = [int(i) for i in cap]
            query = query.where(r.capacity >= cap[0])
            query = query.where(r.capacity <= cap[1])

        
        pri = request.form.get('price')
        if pri!=None:
            price = pri.split(', ')
            price = [int(i) for i in price]
            query = query.where(r.price >= price[0])
            query = query.where(r.price <= price[1])
        
        cnt = request.form.get('roomcount')
        if cnt!=None:
            count = cnt.split(', ')
            count = [int(i) for i in count]
            query = query.where(subquery.count >= count[0])
            query = query.where(subquery.count <= count[1])
        
        rating = request.form.get('category')
        if rating!="any":
            query = query.where(hotel.rating == int(rating))
        
        chain = request.form.get('hotelchain')
        if chain!="any":
            query = query.where(hotelchain.chainname == str(chain))
        
        address = request.form.get('area')
        if address!="any":
            query = query.where(hotel.address == str(address))

        rooms = db.session.execute(text(str(query))).mappings().all()

        hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
        hotels = db.session.execute(text('select * from hotel')).mappings().all()

        return render_template("index.html", rooms=rooms, len=len(rooms), hotelchains=hotelchains, numhotelchains=len(hotelchains), hotels=hotels, numhotels=len(hotels))

    hotelchains = db.session.execute(text('select * from hotelchain')).mappings().all()
    hotels = db.session.execute(text('select * from hotel')).mappings().all()
    rooms = db.session.execute(text('select * from luxury')).mappings().all()
    return render_template("index.html", rooms=rooms, len=len(rooms), hotelchains=hotelchains, numhotelchains=len(hotelchains), hotels=hotels, numhotels=len(hotels))


@app.route("/transformbooking", methods=["GET", "POST"])
def transformbooking():
    if request.method == "POST":
        booking_table = Table('booking')
        booking_query = Query.from_(booking_table).select('*').where(booking_table.bookingid==request.form.get('bookingid'))
        booking = db.session.execute(text(str(booking_query))).mappings().all()
        rental = Table('rental')

        query = Query.into(rental).insert(booking[0]["bookingid"], booking[0]["roomid"], booking[0]["hotelid"], request.form.get('ssn'), booking[0]["startdate"], booking[0]["enddate"], booking[0]["numberguests"])
        print(query)
        db.session.execute(text(str(query)))
        db.session.commit()

        bookings = db.session.execute(text('select * from booking')).mappings().all()
        return render_template("transformbooking.html", bookings=bookings, numbookings=len(bookings))

    bookings = db.session.execute(text('select * from booking')).mappings().all()
    return render_template("transformbooking.html", bookings=bookings, numbookings=len(bookings))


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080)


