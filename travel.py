from flask import Flask, render_template, json, request,redirect,url_for,session
from flaskext.mysql import MySQL
from my_utils import verbose_print, error_print
import random
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

class Group:
    
    def __init__(self, travel, dest, agent, passenger):
        self.travel = travel
        self.dest = dest
        self.agent = agent
        self.passenger = passenger

class Agent:

    def __init__(self, first_name, last_name, phone_number, email):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email

class Travel:

    def __init__(self, travel_type, travel_class, price, car_rental, depart_date, return_date):
        self.travel_type = travel_type
        self.travel_class = travel_class
        self.price = price
        self.car_rental = car_rental
        self.depart_date = depart_date
        self.return_date = return_date

class Car_Rental:

    def __init__(self, class_type, num_days, price):
        self.class_type = class_type
        self.num_days = num_days
        self.price = price

class Location:

    def __init__(self, state, country, city_name):
        self.state = state
        self.country = country
        self.city_name = city_name

class Review:

    def __init__(self, username, rating, review):
        self.username = username
        self.rating = rating
        self.review = review

@app.route("/")
@app.route("/index", methods=['GET','POST'])
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

@app.route('/showLogin', methods=['GET','POST'])
def showLogin():
    return render_template('signin.html')

@app.route('/login', methods=['POST'])
def login():

    conn = mysql.get_db()
    cursor = conn.cursor()

    email = request.form['inputEmail']
    password = request.form['inputPassword']

    sql = "SELECT `group`.`group_id` FROM `passenger`, `group` WHERE `email` = %s and `passkey` = %s"
    cursor.execute(sql, (email, password))
    data = cursor.fetchone()
    
    if data == None:
        return render_template('signin.html', failed=True)
    else:
        session['group_id'] = data[0]
        return redirect(url_for('showTripsPage'))

@app.route('/showTripsPage')
def showTripsPage():

    conn = mysql.get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM `group` WHERE `group`.`group_id` = %s"
    cursor.execute(sql, (session.get('group_id', None)))
    data = cursor.fetchall()

    #Grab data from returned tuple
    group_data = data[0]
    travel_agent_id = group_data[3]
    cruise_id = group_data[4]
    car_rental_id = group_data[5]
    flight_id = group_data[6]
    dest_loc = group_data[7]

    sql = "SELECT * FROM `travel_agent` WHERE `agent_id` = %s"
    cursor.execute(sql, (travel_agent_id))
    data = cursor.fetchall()
    agent_data = data[0]
    agent = Agent(agent_data[1], agent_data[2], agent_data[3], agent_data[4])

    car_rental = None
    if car_rental_id != None:
        sql = "SELECT * FROM `car_rental` WHERE `car_rental_id` = %s"
        cursor.execute(sql, (car_rental_id))
        data = cursor.fetchall()
        car_data = data[0]
        car_rental = Car_Rental(car_data[2], car_data[4], car_data[1])

    if cruise_id != None:
        sql = "SELECT * FROM `cruise` WHERE `cruise_id` = %s"
        cursor.execute(sql, (cruise_id))
        data = cursor.fetchall()
        cruise_data = data[0]
        travel = Travel("Cruise", cruise_data[2], cruise_data[1], car_rental, cruise_data[3], cruise_data[4])
    elif flight_id != None:
        sql = "SELECT * FROM `flight` WHERE `flight_id` = %s"
        cursor.execute(sql, (flight_id))
        data = cursor.fetchall()
        flight_data = data[0]
        travel = Travel("Flight", flight_data[2], flight_data[3], car_rental, flight_data[4], flight_data[5])

    sql = "SELECT * FROM `location` WHERE `location_id` = %s"
    cursor.execute(sql, (dest_loc))
    data = cursor.fetchall()
    location_data = data[0]
    location = Location(location_data[1], location_data[2], location_data[3])

    session['location_id'] = dest_loc
    session['location_data'] = location
    
    return render_template('userviewtrips.html', agent = agent, car_rental = car_rental, travel = travel, location = location)

@app.route('/showReviews', methods =['GET','POST'])
def showReviews():
    session['location'] = request.form['location']

    conn = mysql.get_db()
    cursor = conn.cursor()
    sql = "SELECT `location_id` from `location` WHERE `country` = %s"
    cursor.execute(sql, (request.form['location']))
    data = cursor.fetchone()
    location_id = data[0]

    sql = "SELECT * from `reviews` WHERE `location_id` = %s"
    cursor.execute(sql, (location_id))
    data = cursor.fetchall()
    review_array = []
    for review_tuple in data:
        review = Review(review_tuple[1], review_tuple[2], review_tuple[3])
        review_array.append(review)
    
    return render_template('reviews.html', location = request.form['location'], reviews = review_array)  

@app.route('/addReview', methods = ['POST'])
def addReview():

    #REVIEWS
    username = request.form['review-name']
    rating = request.form['star-count']
    review = request.form['review-comment']
    location_id = session.get('location_id', None)

    conn = mysql.get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO `reviews`(`username`, `rating`, `detailed_review`, `location_id`) VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (username, rating, review, location_id))

    conn.commit()
    return redirect(url_for('index'))

@app.route('/showTripForm', methods=['GET','POST'])
def showTripForm():
    session['location'] = request.form['location']
    return render_template('booktrip.html', location = request.form['location'])

@app.route('/showTripFormNoRequest', methods=['GET','POST'])
def showTripFormNoRequest():
    return render_template('booktrip.html', location = session.get('location', None))

@app.route('/bookTrip', methods=['POST'])
def bookTrip():
    # Use this to get the dest location
    dest_location_str = session.get('location', None)
    print(dest_location_str)

    #GROUP
    group_name = request.form['groupName']
    session['group_name'] = group_name
    passkey = request.form['password']

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
    ccMonth = request.form['cc-month']
    ccYear = request.form['cc-year']
    ccCVV = request.form['cc-cvv']
    paymentMethod = request.form['paymentMethod']
    print(paymentMethod)
    ccExp = ccMonth + "/" + ccYear

    conn = mysql.get_db()
    cursor = conn.cursor()
    sql_fetchid = "SELECT LAST_INSERT_ID();"

    #check if given source location already exists before inserting
    sql = "SELECT `location_id` FROM `location` WHERE `state` = %s AND `country` = %s AND `city_name` = %s"
    cursor.execute(sql, (state, country, city))
    data = cursor.fetchone()

    if data == None:
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

    sql = "INSERT INTO `payment`(`card_expr_date`, `card_num`, `payment_type`) VALUES (%s,%s,%s)"
    cursor.execute(sql, (ccExp, ccNumber, paymentMethod))
    cursor.execute(sql_fetchid);
    data = cursor.fetchone()
    payment_id = data[0]
    
    sql = '''INSERT INTO `group`(`group_size`, `passkey`, `payment_id`, `travel_agent_id`,
    `source_location`, `dest_location`) VALUES (%s,%s,%s,%s,%s,%s)'''
    cursor.execute(sql, (0, passkey, payment_id, travel_agent_id, sourceloc_id, destloc_id))
    cursor.execute(sql_fetchid)
    data = cursor.fetchone()
    group_id = data[0]
    
    sql = '''INSERT INTO `passenger`(`first_name`,`last_name`,`email`, `age`,
    `phone_number`, `group_id`) VALUES (%s,%s,%s,%s,%s,%s)'''
    cursor.execute(sql, (first_name, last_name, email, age, phone_number, group_id))
    conn.commit()

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
    `phone_number`,`group_id`) VALUES (%s,%s,%s,%s,%s,%s)'''
    cursor.execute(sql, (first_name, last_name, email, age, phone_number, session.get('group_id', None)))

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
    #Travel
    transport_mode = request.form['transport-mode']
    transport_class = request.form['class']
    dep_month = request.form['dep-month']
    dep_day = request.form['dep-day']
    dep_time = request.form['dep-time']
    ret_month = request.form['ret-month']
    ret_day = request.form['ret-day']
    ret_time = request.form['ret-time']

    dep_date = "2018-" + dep_month + "-" + dep_day + " " + dep_time + ":00:00"
    ret_date = "2018-" + ret_month + "-" + ret_day + " " + ret_time + ":00:00"

    conn = mysql.get_db()
    cursor = conn.cursor()
    sql_fetchid = "SELECT LAST_INSERT_ID();"

    flight_no = random.randint(1000, 9999)

    if transport_class == "Economy":
        price = 250
    elif transport_class == "Business":
        price = 500
    elif transport_class == "Luxury":
        price = 1000

    flight_id = None
    cruise_id = None
    car_rental_id = None

    print(transport_mode)
    
    if transport_mode == "Flight":
        sql = "INSERT INTO `flight`(`flight_no`, `class`, `price`, `depart_date`, `return_date`) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql, (flight_no, transport_class, price, dep_date, ret_date))
        cursor.execute(sql_fetchid)
        data = cursor.fetchone()
        flight_id = data[0]
    elif transport_mode == "Cruise":
        sql = "INSERT INTO `cruise`(`price`, `class`, `depart_date`, `return_date`) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, (price, transport_class, dep_date, ret_date))
        cursor.execute(sql_fetchid)
        data = cursor.fetchone()
        cruise_id = data[0]    

    if request.form.get('car-check'):
        print("Checked")
        car_class = request.form['car-class']
        rental_days = request.form['car-days']

        if car_class == "Standard":
            car_price = 50 * int(rental_days)
        elif car_class == "Luxury":
            car_price = 150 * int(rental_days)

        sql = "INSERT INTO `car_rental`(`price`, `class`, `days_rented`) VALUES (%s,%s,%s)"
        cursor.execute(sql, (car_price, car_class, rental_days))
        cursor.execute(sql_fetchid)
        data = cursor.fetchone()
        car_rental_id = data[0]


    group_id = session.get('group_id', None)
    sql = "UPDATE `group` SET `flight_id` = %s, `cruise_id` = %s, `car_rental_id` = %s WHERE `group_id` = %s"
    cursor.execute(sql, (flight_id, cruise_id, car_rental_id, group_id))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug = True)
