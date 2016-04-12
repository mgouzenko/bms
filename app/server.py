#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, make_response

from models import entrants, residents, vehicles

tmpl_dir = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)


# The following is a dummy URI that does not connect to a valid database. You
# will need to modify it to connect to your Part 2 database in order to use the
# data.
#
# The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2

DBURI = 'postgresql://mag2272:C9qlubhnlN@w4111a.eastus.cloudapp.azure.com/proj1part2'
engine = create_engine(DBURI)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request (every time you
    enter an address in the web browser).  We use it to setup a database
    connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database
    connection.  If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request
    information:

    request.method:   "GET" or "POST" request.form:     if the browser submitted
    a form, this contains the data in the form request.args:     dictionary of
    URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """
    return render_template('home.html')


@app.route('/another')
def another():
    return render_template("another.html")

# Example of adding new data to the database


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
    return redirect('/')


@app.route('/login/<entity_type>', methods=['GET', 'POST'])
def login(entity_type):
    user_id = request.cookies.get('user_id')
    if user_id:
        return redirect('/resident_dashboard/{}'.format(user_id))
    if request.method == 'POST':
        username = request.form.get('username')
        resident = residents.find_by_username(username, g.conn) if username else None
        if resident:
            resp = make_response(
                    redirect('/resident_dashboard/{}'.format(
                        resident.entrant_id)))
            resp.set_cookie('user_id', value=str(resident.entrant_id))
            resp.set_cookie('entity_type', entity_type)
            return resp
    return render_template('login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('user_id', '', expires=0)
    resp.set_cookie('entity_type', '', expires=0)
    return resp

@app.route('/resident_dashboard/<user_id>')
def route_to_guests(user_id):
    return redirect('/resident_dashboard/{}/guests'.format(user_id))

@app.route('/resident_dashboard/<user_id>/<dash_type>')
def display_dashboard(user_id, dash_type):
    entity_type = request.cookies.get('entity_type')
    if user_id != request.cookies.get('user_id') and entity_type != 'residents':
        return redirect('/')
    resident = residents.find_by_id(user_id, g.conn)

    if dash_type == 'guests':
        guests = resident.get_guests(g.conn)
        return render_template(
                'resident_dashboard_guests.html',
                resident=resident,
                guests=guests,
                entity_type="Resident")

    elif dash_type == 'cars':
        cars = resident.get_cars(g.conn)
        map(lambda c: c.get_drivers(g.conn), cars)
        return render_template(
                'resident_dashboard_cars.html',
                resident=resident,
                cars=cars,
                entity_type="Resident")

    return redirect('/')

@app.route('/car/<state>/<license_plate>/', methods=['GET', 'POST'])
def car(state, license_plate):
    if request.method == 'POST':
        print 'unimplemented'

    car = vehicles.find_by_license_plate(g.conn, state, license_plate)

    if(car != None):
        return render_template('edit_car.html', car=car)
    else:
        return render_template('error.html', error_desc="That car was not found.")

@app.route('/car/<state>/<license_plate>/update_car', methods=['POST'])
def update_car(state, license_plate):
    # Update the database based on the form data
    g.conn.execute(
        'UPDATE vehicles\
         SET make = \'' + request.form["make"] + '\'\
         WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    g.conn.execute(
        'UPDATE vehicles\
         SET model = \'' + request.form["model"] + '\'\
         WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    g.conn.execute(
        'UPDATE vehicles\
         SET color = \'' + request.form["color"] + '\'\
         WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    if(request.form["default_spot"] != None and request.form["default_spot"] != ""):
        g.conn.execute(
            'UPDATE vehicles\
             SET default_spot = \'' + request.form["default_spot"] + '\'\
             WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')
    else:
        g.conn.execute(
            'UPDATE vehicles\
             SET default_spot = NULL \
             WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')


    print license_plate
    return redirect('/car/' + state + '/' + license_plate)

@app.route('/car/<state>/<license_plate>/park_car', methods=['POST'])
def park_car(state, license_plate):
    if(request.form["spot_number"] != None and request.form["spot_number"] != "" and request.form["key_number"] != None and request.form["key_number"] != ""):
        g.conn.execute(
            'UPDATE vehicles\
             SET spot_number = \'' + request.form["spot_number"] + '\'\
             WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')
        g.conn.execute(
            'UPDATE vehicles\
             SET key_number = \'' + request.form["key_number"] + '\'\
             WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    return redirect('/car/' + state + '/' + license_plate)

@app.route('/<int:provider_id>/business_dashboard', methods=['GET', 'POST'])
def business_dashboard(provider_id):
    if request.method == 'POST':

        # Update the database based on the form data
        g.conn.execute(
            'UPDATE service_providers\
             SET business_description = \'' + request.form["description"] + '\'\
             WHERE business_id = ' + str(provider_id))

        g.conn.execute(
            'UPDATE service_providers\
             SET email = \'' + request.form["email"] + '\'\
             WHERE business_id = ' + str(provider_id))

        g.conn.execute(
            'UPDATE service_providers\
             SET phone_num = \'' + request.form["phone_num"] + '\'\
             WHERE business_id = ' + str(provider_id))

        # Clear the serviced buildings for this particular business
        g.conn.execute(
            'DELETE FROM ONLY provides_services_for AS psf\
             WHERE psf.business_id = ' + str(provider_id))

        # Add the selected buildings to the list of buildings that this business services
        for serviced_building in request.form.getlist("building"):
            g.conn.execute(
                'INSERT INTO provides_services_for (business_id, building_id) VALUES\
                 (' + str(provider_id) + ", " + str(serviced_building) + ")")

    # Verify that we are logged in as a service provider.
    business_cursor = g.conn.execute(
        'SELECT sp.business_id, sp.business_name, sp.business_description, sp.phone_num, sp.email \
         FROM service_providers sp \
         WHERE sp.business_id = ' + str(provider_id))

    business = business_cursor.fetchone()

    if (business != None):
        buildings_cursor = g.conn.execute(
            'SELECT buildings.building_name, buildings.building_id \
             FROM buildings')

        buildings = []

        for record in buildings_cursor:

            check_service_cursor = g.conn.execute(
                'SELECT psf.business_id, psf.building_id \
                 FROM provides_services_for psf \
                 WHERE psf.business_id = ' 
                + str(business.business_id) + "AND psf.building_id = " + str(record.building_id))

            building_entry = dict(record)

            if(check_service_cursor.fetchone() != None):
                building_entry['service_available'] = "checked"
            else:
                building_entry['service_available'] = ""

            buildings.append(building_entry)

        cur_description = "This is the description currently in the database."
        return render_template('business_dashboard.html', buildings=buildings, business=business)
    else:
        return render_template('error.html', error_desc="This user is not a business.")

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
