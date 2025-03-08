import os
import datetime
from flasgger import Swagger
from flask import Flask, request, jsonify, redirect
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from client.citypower import CityPowerAPI

APPLICATION = "loadshedding"
VERSION = "2.0.0"

DEBUG = os.environ.get("DEBUG_ENABLED", False) == "true"
SSL = os.environ.get("SSL_ENABLED", False) == "true"
app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

swagger_config = {
    "headers": [],
    "title": APPLICATION,
    "version": VERSION,
    "swagger_ui": True,
    "description": "Joburg City Power Loadshedding Schedule API",
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/characteristics/static",
}

swagger = Swagger(app, config=swagger_config)

HTTP_CLIENT = CityPowerAPI()

STAGES = {}
# for i in range(1, 17):
#     schedule = []
#     with open(f'eskom-calendar/generated/city-power-{i}.csv') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         line_count = 0
#         for row in csv_reader:
#             if line_count == 0:
#                 line_count += 1
#             else:
#                 schedule.append({
#                     'date_of_month': row[0],
#                     'start_time': row[1],
#                     'finish_time': row[2],
#                     'stage': int(row[3])
#                 })
#                 line_count += 1
#     STAGES[f'stage-{i}'] = schedule


@app.route("/", methods=["GET"])
def root():
    return redirect("/apidocs", code=308)


@app.route("/schedule-for-block/<block>", methods=["GET"])
def get_schedule_for_block(block):
    """Get loadshedding schedule for chosen block
    ---
    parameters:
      - name: block
        in: path
        type: string
        required: true
    definitions:
     Health:
       type: object
       properties:
         application:
           type: string
         version:
           type: string
    responses:
     200:
       description:
       content:
         application/json:
           schema:
             $ref: '#/definitions/Health'
    """
    current_stage = HTTP_CLIENT.get_current_active_stage()

    d = datetime.datetime.now()
    today = d.strftime("%d")

    slots_all = list(
        map(
            lambda y: (
                {"start_time": y["start_time"], "finish_time": y["finish_time"]}
            ),
            filter(
                lambda x: (x["stage"] <= current_stage and x["date_of_month"] == today),
                STAGES[f"stage-{block}"],
            ),
        )
    )
    slots = list({v["start_time"]: v for v in slots_all}.values())
    return jsonify({"schedule": slots, "day": today, "current_stage": current_stage})


@app.route("/schedule", methods=["GET"])
def get_schedule():
    """Get full loadshedding schedule
    ---
    definitions:
     Health:
       type: object
       properties:
         application:
           type: string
         version:
           type: string
    responses:
     200:
       description:
       content:
         application/json:
           schema:
             $ref: '#/definitions/Health'
    """
    return jsonify(STAGES)


@app.route("/stage", methods=["GET"])
def get_stage():
    """Get current CityPower loadshedding stage
    ---
    definitions:
     Health:
       type: object
       properties:
         application:
           type: string
         version:
           type: string
    responses:
     200:
       description:
       content:
         application/json:
           schema:
             $ref: '#/definitions/Health'
    """
    return jsonify({"current_stage": HTTP_CLIENT.get_current_active_stage()})


@app.route("/health", methods=["GET"])
def health():
    """Get service health
    ---
    definitions:
      Health:
        type: object
        properties:
          application:
            type: string
          version:
            type: string
    responses:
      200:
        description:
        content:
          application/json:
            schema:
              $ref: '#/definitions/Health'
    """
    return {"application": APPLICATION, "version": VERSION, "debug": DEBUG, "ssl": SSL}


if __name__ == "__main__":
    context = None
    if SSL:
        context = ("/etc/ssl/certs/host.crt", "/etc/ssl/certs/host.key")
    app.run(debug=DEBUG, host="0.0.0.0", port=21445, threaded=True, ssl_context=context)
