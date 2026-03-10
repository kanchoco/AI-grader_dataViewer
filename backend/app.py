import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google.cloud.sql.connector import Connector
import sqlalchemy
import pandas as pd
import uuid
from ai_grader import run_ai_grading


# React build 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_BUILD_PATH = os.path.join(BASE_DIR, "dist")

# Flask app
app = Flask(
    __name__,
    static_folder=FRONTEND_BUILD_PATH,
    static_url_path=""
)

CORS(app)

# 환경변수 (Cloud Run)
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]
CONN_NAME = os.environ["CONN_NAME"] 

connector = Connector()

# Cloud SQL 연결
def get_engine():
    def getconn():
        return connector.connect(
            CONN_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME
        )

    return sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_pre_ping=True,
    )

# API 영역

@app.get("/student/<student_id>")
def get_student(student_id):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            sqlalchemy.text("SELECT * FROM studentDB WHERE student_id = :id"),
            {"id": student_id}
        ).mappings().fetchone()

        if not row:
            return {"error": "student not found"}, 404

        return jsonify(dict(row)) 

# 프런트엔드 서빙
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_BUILD_PATH, "index.html")

@app.route("/<path:path>")
def serve_react(path):
    file_path = os.path.join(FRONTEND_BUILD_PATH, path)
    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_BUILD_PATH, path)
    return send_from_directory(FRONTEND_BUILD_PATH, "index.html")