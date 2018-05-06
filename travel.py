from flask import Flask, render_template, json, request,redirect,url_for,session
from flaskext.mysql import MySQL
from my_utils import verbose_print, error_print
app = Flask(__name__)
mysql = MySQL()

#jinja2 for html dynamic changing

# configs
app.config['MYSQL_DATABASE_USER'] = 'jack'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jacksquared'
app.config['MYSQL_DATABASE_DB'] = 'travel_agency'
app.config['MYSQL_DATABASE_HOST'] = 'travelagency.cgydjwsxgwz6.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.secret_key = "super secret key"
mysql.init_app(app)

@app.route("/")
@app.route("/index")
def index():
    conn = mysql.get_db()
    cursor = conn.cursor()

    num_visits = []
    locations = ["Hawaii", "Russia", "Australia", "France", "Greenland", "Japan"]
    
    for loc in locations:
        sql = "SELECT `num_visits` FROM `location` WHERE `country` = %s"
        cursor.execute(sql, loc)
        data = cursor.fetchone()
        num_visits.append(data[0])
        
    return render_template('index.html', v_hawaii = num_visits[0], v_russia = num_visits[1], v_australia = num_visits[2], v_france = num_visits[3], v_greenland = num_visits[4], v_japan = num_visits[5])

@app.route('/showTripForm', methods=['POST'])
def showTripForm():
    session['location'] = request.form['location']
    return render_template('booktrip.html', location = request.form['location'])

@app.route('/showLogin', methods=['POST'])
def showLogin():
    return render_template('signin.html')

@app.route('/login', methods=['POST'])
def login():
    return render_template('signin.html', failed=True)

@app.route('/bookTrip', methods=['POST'])
def bookTrip():
    # Use this to get the dest location
    dest_location_str = session.get('location', None)
    print(dest_location_str)

    #GROUP
    group_name = request.form['groupName']
    session['group_name'] = group_name

    #PASSENGER
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    phone_number = request.form['phoneNumber']
    age = request.form['age']
    email = request.form['email']

    #SOURCE LOCATION
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']

    #PAYMENT INFO
    ccNumber = request.form['cc-number']
    ccExp = request.form['cc-expiration']
    ccCVV = request.form['cc-cvv']

    conn = mysql.get_db()
    cursor = conn.cursor()
    sql_fetchid = "SELECT LAST_INSERT_ID();"

    #check if given source location already exists before inserting
    sql = "SELECT `location_id` FROM `location` WHERE `state` = %s AND `country` = %s AND `city_name` = %s"
    cursor.execute(sql, (state, country, city))
    data = cursor.fetchone()

    if data[0] == None:
        sql = "INSERT INTO `location`(`state`, `country`, `city_name`) VALUES (%s,%s,%s)"
        cursor.execute(sql, (state, country, city))
        cursor.execute(sql_fetchid);
        data = cursor.fetchone()
        sourceloc_id = data[0]
    else:
        sourceloc_id = data[0]

    sql = "SELECT `location_id` FROM `location` WHERE `country` = %s"
    cursor.execute(sql, dest_location_str)
    data = cursor.fetchone()
    destloc_id = data[0]

    #ensures even balancing of travel agents by picking the one with the lowest amount of groups assigned
    sql = "SELECT travel_agent_id, COUNT(1) AS `num` FROM `group` GROUP BY travel_agent_id ORDER BY `num` ASC"
    cursor.execute(sql)
    data = cursor.fetchone()
    travel_agent_id = data[0]
    
    sql = "INSERT INTO `group`(`group_size`, `travel_agent_id`, `source_location`, `dest_location`) VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (0, travel_agent_id, sourceloc_id, destloc_id))
    cursor.execute(sql_fetchid)
    data = cursor.fetchone()
    group_id = data[0]
    
    sql = "INSERT INTO `payment`(`card_expr_date`, `card_num`, `payment_type`) VALUES (%s,%s,%s)"
    cursor.execute(sql, (ccExp, ccNumber, "Credit"))
    cursor.execute(sql_fetchid);
    data = cursor.fetchone()
    payment_id = data[0]
    
    sql = '''INSERT INTO `passenger`(`first_name`,`last_name`,`email`, `age`,
    `phone_number`, `payment_id`, `group_id`) VALUES (%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute(sql, (first_name, last_name, phone_number, age, email, payment_id, group_id))
    conn.commit()

    session['payment_id'] = payment_id
    session['group_id'] = group_id
    
    if request.form.get('another-guest'):
        return redirect(url_for('addGuestForm'))
    else:
        return redirect(url_for('showTransportForm'))

@app.route('/addGuestForm')
def addGuestForm():
    return render_template('addguest.html', group_name = session.get('group_name', None))

@app.route('/addGuest', methods=['GET','POST'])
def addGuest():

    #PASSENGER
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    phone_number = request.form['phoneNumber']
    age = request.form['age']
    email = request.form['email']
    
    conn = mysql.get_db()
    cursor = conn.cursor()
    sql = '''INSERT INTO `passenger`(`first_name`,`last_name`,`email`, `age`,
    `phone_number`, `payment_id`, `group_id`) VALUES (%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute(sql, (first_name, last_name, phone_number, age, email,
    session.get('payment_id', None), session.get('group_id', None)))

    conn.commit()
    if request.form.get('another-guest'):
        return redirect(url_for('addGuestForm'))
    else:
        return redirect(url_for('showTransportForm'))

@app.route('/showTransportForm')
def showTransportForm():
    return render_template('choosetransport.html', group_name = session.get('group_name', None))

@app.route('/chooseTransport', methods=['POST'])
def chooseTransport():
    print('Booked')
    # use reqeust.form.get('name_of_button_input') to get if checked. Use this to popualte database
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug = True)
