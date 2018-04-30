from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from my_utils import verbose_print, error_print
app = Flask(__name__)
mysql = MySQL()

# configs
app.config['MYSQL_DATABASE_USER'] = 'jack'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jacksquared'
app.config['MYSQL_DATABASE_DB'] = 'travel_agency'
app.config['MYSQL_DATABASE_HOST'] = 'travelagency.cgydjwsxgwz6.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)


@app.route("/")
def main():
    return render_template('booktrip.html')

@app.route('/goToIndex')
def showSignUp():
    return render_template('index.html')

@app.route('/bookTrip', methods=['POST'])
def bookTrip():
    #GROUP
    group_name = request.form['groupName']

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
    
    sql = "INSERT INTO `location`(`state`, `country`, `city_name`) VALUES (%s,%s,%s)"
    cursor.execute(sql, (state, country, city))
    cursor.execute(sql_fetchid);
    data = cursor.fetchone()
    sourceloc_id = data[0]
    
    sql = "INSERT INTO `group`(`group_size`, `travel_agent_id`, `source_location`) VALUES (%s,%s,%s)"
    cursor.execute(sql, (1, 1, sourceloc_id))
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
    return json.dumps({'message': 'Tables updated successfully !'})

if __name__ == "__main__":
    app.run()
