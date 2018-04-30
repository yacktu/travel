from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from my_utils import verbose_print, error_print
app = Flask(__name__)
mysql = MySQL()

verbose = True

# configs
app.config['MYSQL_DATABASE_USER'] = 'jack'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jacksquared'
app.config['MYSQL_DATABASE_DB'] = 'travel_agency'
app.config['MYSQL_DATABASE_HOST'] = 'travelagency.cgydjwsxgwz6.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/goToIndex')
def showSignUp():
    return render_template('index.html')

@app.route('/bookTrip', methods=['POST'])
def bookTrip():
    if verbose:
        verbose_print('In Book Trip Function')

    #GROUP
    group_name = request.form['groupName']
    if verbose:
        verbose_print('Group Name: {}'.format(group_name))

    #PASSENGER
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    phone_number = request.form['phoneNumber']
    age = request.form['age']
    email = request.form['email']

    if verbose:
        verbose_print('First Name: {}'.format(first_name))
        verbose_print('Last Name: {}'.format(last_name))
        verbose_print('Phone Number: {}'.format(phone_number))
        verbose_print('Age: {}'.format(age))
        verbose_print('Email: {}'.format(email))

    #SOURCE LOCATION
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']

    if verbose:
        verbose_print('Country: {}'.format(country))
        verbose_print('State: {}'.format(state))
        verbose_print('City: {}'.format(city))

    #PAYMENT INFO
    ccNumber = request.form['cc-number']
    ccExp = request.form['cc-expiration']
    ccCVV = request.form['cc-cvv']

    if verbose:
        verbose_print('CC-Num: {}'.format(ccNumber))
        verbose_print('CC-Exp: {}'.format(ccExp))
        verbose_print('CC-VV: {}'.format(ccCVV))

    conn = mysql.get_db()
    print(conn)
    cursor = conn.cursor()
    print(cursor)
    sql = "INSERT INTO `passenger`(`first_name`,`last_name`,`email`, `age`, `phone_number`) VALUES (%s,%s,%s,%s,%s)"
    print(sql)
    cursor.execute(sql, (first_name, last_name, phone_number, age, email))

    print("Excecuted SQL")

    data = cursor.fetchall()
    if len(data) is 0:
        conn.commit()
        return json.dumps({'message': 'Flight created successfully !'})
    else:
        return json.dumps({'error': str(data[0])})

if __name__ == "__main__":
    app.run()
