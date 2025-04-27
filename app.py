from flask import Flask, render_template, request

app = Flask(__name__)

passphrase = "admin123" # na razie tutaj na sztywno, maly priorytet
ip_alarm = "http://127.0.0.1:5001" # na razie tez na sztywno, pomyslec co z tym, moze wpisywanie po zalogowaniu jesli ma byc elastyczne

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if request.form["password"] == passphrase:
            return render_template("panel.html", ip_alarm=ip_alarm, passphrase=passphrase)
        else:
            return render_template("login.html", error="Nieprawidłowe hasło.")

if __name__ == "__main__":
    app.run()

