from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
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
    sql = "INSERT INTO `passenger`(`first_name`,`last_name`,`email`, `age`, `phone_number`) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(sql, (first_name, last_name, phone_number, age, email))

    data = cursor.fetchall()
    if len(data) is 0:
        conn.commit()
        return json.dumps({'message': 'Flight created successfully !'})
    else:
        return json.dumps({'error': str(data[0])})

if __name__ == "__main__":
    app.run()
