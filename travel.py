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


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    _flight_carrier = request.form['inputName']
    _class = request.form['inputEmail']
    _price = request.form['inputPassword']

    if _flight_carrier and _class and _price:

        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.callproc('new_procedure', (_flight_carrier, _class, _price))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return json.dumps({'message': 'Flight created successfully !'})
        else:
            return json.dumps({'error': str(data[0])})

    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})


if __name__ == "__main__":
    app.run()
