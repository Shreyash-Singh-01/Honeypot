import logging
from flask import Flask, request, render_template, redirect, url_for
from logging.handlers import RotatingFileHandler


def setup_logger():
    logger = logging.getLogger("funnellogger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler = RotatingFileHandler(
            "audits.log",
            maxBytes=2000,
            backupCount=5
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


funnel_logger = setup_logger()



def create_web_honeypot(input_username="admin", input_password="password"):
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["POST"])
    def login():
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

        funnel_logger.info(
            f'IP={ip_address} USER="{username}" PASS="{password}"'
        )

       
        return redirect(url_for("fake_dashboard"))

    @app.route("/dashboard")
    def fake_dashboard():
        return "<h1>Internal Portal</h1><p>Loading resources...</p>"

    return app



def run_web_honeypot(port=5000, input_username="admin", input_password="password"):
    app = create_web_honeypot(input_username, input_password)
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run_web_honeypot()
