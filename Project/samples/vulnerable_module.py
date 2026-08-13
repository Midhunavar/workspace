import sqlite3

API_KEY = "sk-live-hardcoded-secret-abc123"


def run_query(user_input):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % user_input)
    return cursor.fetchall()


def calculate(expression):
    return eval(expression)


class PaymentProcessor:
    def charge(self, amount):
        return {"status": "ok", "amount": amount}
