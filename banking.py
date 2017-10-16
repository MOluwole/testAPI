import random

import pymysql
from flask import jsonify, request, Flask

app = Flask(__name__)
connection = pymysql.connect(host='localhost', user='root', password='nigeriA070', db='banking', charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def get_account():
    account_number = ""
    for i in range(10):
        account_number += str(random.randint(1, 10))
    return account_number


@app.route('/banking/login', methods=['GET'])
def login():
    try:
        username = request.args.get('username')
        password = request.args.get('password')

        print username

        sql = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor = connection.cursor()
        cursor.execute(sql, (username, password))
        result = cursor.fetchall()

        if int(len(result)) > 0:
            name = str(result[0]['name'].encode('ascii', 'ignore'))
            account_number = str(result[0]['account_number'].encode('ascii', 'ignore'))
            return jsonify({'message': 'Login Successful', 'name': name, 'account_number': account_number,
                            'success': 1})
        else:
            return jsonify({'message': 'Invalid Login Details', 'success': 0})
    except:
        return jsonify({'message': 'An Error Occurred. Please Try again', 'success': 0})


@app.route('/banking/register', methods=['GET'])
def register():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        full_name = request.args.get('name')
        phone_number = request.args.get('phone_number')
        address = request.args.get('address')

        account_number = get_account()

        sql = "SELECT * from users WHERE username = %s"
        curr = connection.cursor()
        curr.execute(sql, username)
        res = curr.fetchall()

        if int(len(res)) <= 0:
            sql = "INSERT INTO users(name, username, password, num, address, account_number) VALUES(%s, " \
                  "%s, %s, %s, %s, %s)"
            cursor = connection.cursor()
            cursor.execute(sql, (full_name, username, password, phone_number, address, account_number))
            connection.commit()

            sql = "INSERT INTO account(account_number, balance) VALUES(%s, %s)"
            cur = connection.cursor()
            cur.execute(sql, (account_number, '100000'))
            connection.commit()

            return jsonify({'message': 'Registration Successfully', 'name': full_name, 'account_number': account_number,
                            'success': 1})
        else:
            return jsonify({'message': 'Username already exists in database. Choose a Unique Username', 'success': 0})
    except Exception:
        return jsonify({'message': 'Could not complete Registration. Try Again', 'success': 0})


@app.route('/banking/changepassword', methods=['GET'])
def change_password():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        new_password = request.args.get('new_password')

        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (username, password))
        result = cursor.fetchall()

        if int(len(result)) > 0:
            sql = "UPDATE users SET password = %s WHERE username = %s"
            cur = connection.cursor()
            cur.execute(sql, (username, password))
            connection.commit()
            return jsonify({'message': 'Password Changed Successfully', 'success': 1})
        else:
            return jsonify({'message': 'Login Credentials invalid. Please Provide your authentic login credentials',
                            'success': 0})
    except Exception:
        return jsonify({'message': 'An unexpected error occurred. Try Again', 'success': 0})


@app.route('/banking/balance', methods=['GET'])
def balance():
    try:
        account_number = request.args.get('account_number')

        sql = "SELECT * FROM account WHERE account_number = %s"
        cursor = connection.cursor()
        cursor.execute(sql, account_number)
        result = cursor.fetchall()

        if int(len(result)) > 0:
            account_balance = str(result[0]['balance'].encode('ascii', 'ignore'))
            return jsonify({'balance': account_balance, 'success': 0})
        else:
            return jsonify({'message': 'No record Found for the provided account', 'success': 0})
    except Exception:
        return jsonify({'message': 'An Error Occurred', 'success': 0})


@app.route('/banking/transaction', methods=['GET'])
def transaction():
    try:
        account_number = request.args.get('account_number')
        sql = 'SELECT * FROM transaction WHERE account_number = %s'
        cursor = connection.cursor()
        cursor.execute(sql, account_number)
        result = cursor.fetchall()

        if int(len(result)) > 0:
            transaction_title = str(result[0]['transaction_title'].encode('ascii', 'ignore'))
            transaction_details = str(result[0]['transaction_details'].encode('ascii', 'ignore'))
            amount = str(result[0]['amount'].encode('ascii', 'ignore'))
            dte = str(result[0]['dte'].encode('ascii', 'ignore'))

            return jsonify({'transaction_title': transaction_title, 'transaction_details': transaction_details,
                            'amount': amount, 'dte': dte, 'success': 1})
        else:
            return jsonify({'message': 'No Transaction Record was found', 'success': 0})
    except Exception:
        return jsonify({'message': 'An Unexpected Error Occurred. Try Again', 'success': 0})


@app.route('/banking/transaction/insert', methods = ['GET', 'POST'])
def transaction_insert():
    try:
        account_number = request.args.get('account_number')
        amount = request.args.get('amount')
        title = request.args.get('title')
        details = request.args.get('details')
        dte = request.args.get('date')

        sql = "SELECT balance FROM account WHERE account_number = %s"
        cursor = connection.cursor()
        cursor.execute(sql, account_number)
        result = cursor.fetchall()

        if int(len(result)) > 0:
            balance = str(result[0]['balance'].encode('ascii', 'ignore'))
            if int(amount) > int(balance):
                return jsonify({'message': 'Amount provided for transaction is more than amount in account',
                                'success': 0})
            else:
                remaining_balance = int(balance) - int(amount)
                sql = "INSERT INTO transaction(account_number, transaction_title, transaction_details, amount, dte) " \
                      "VALUES(%s, %s, %s, %s, %s)"
                cursor = connection.cursor()
                cursor.execute(sql, (account_number, title, details, amount, dte))
                connection.commit()

                sql = "UPDATE account SET balance = %s WHERE account_number = %s"
                cur = connection.cursor()
                cur.execute(sql, (remaining_balance, account_number))
                connection.commit()

                return jsonify({'message': 'Transaction Documented successfully', 'success': 0})
        else:
            return jsonify({'message': 'Account not funded.', 'success': 0})
    except Exception:
        return jsonify({'message': 'An unexpected error occurred. Try Again', 'success': 0})

# MEDICAL API's


# @app.route('/medical/login', methods=['GET'])
# def medical_login():
#     try:
#         username = request.args.get('username')
#         password = request.args.get('password')
#
#         sql = "SELECT * FROM users WHERE username = %s AND password = %s"
#         cursor = medical_conn.cursor()
#         cursor.execute(sql, (username, password))
#         result = cursor.fetchall()
#
#         if int(len(result)) > 0:
#             name = str(result[0]['name'].encode('ascii', 'ignore'))
#             return jsonify({'message': 'Login Successful', 'name': name, 'success': 1})
#         else:
#             return jsonify({'message': 'Invalid Login Details. Provide Authentic Login Credentials', 'success': 0})
#     except Exception:
#         return jsonify({'message': 'An Error Occurred. Try Again', 'success': 0})


# @app.route('/medical/register', methods=['GET'])
# def medical_register():
#     try:
#         username = request.args.get('username')
#         password = request.args.get('password')
#         full_name = request.args.get('name')
#         phone_number = request.args.get('phone_number')
#         address = request.args.get('address')
#
#         sql = "SELECT * FROM users WHERE username = %s"
#         cursor = medical_conn.cursor()
#         cursor.execute(sql, username)
#         result = cursor.fetchall()
#
#         if int(len(result)) > 0:
#             return jsonify({'message': 'Username already exists in Database. Provide a unique username', 'success': 0})
#         else:
#             sql = "INSERT INTO users(name, username, password, num, address) VALUES(%s, " \
#                   "%s, %s, %s, %s)"
#             # medical_conn.connect()
#             cursor = medical_conn.cursor()
#             cursor.execute(sql, (full_name, username, password, phone_number, address))
#             medical_conn.commit()
#             return jsonify({'message': 'Registration Successful', 'success': 1})
#     except Exception:
#         return jsonify({'message': 'An Error Occurred. Try Again', 'success': 0})

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
