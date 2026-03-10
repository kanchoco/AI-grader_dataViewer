import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google.cloud.sql.connector import Connector
import sqlalchemy
import pandas as pd
import uuid


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
    
@app.get("/viewer/<rater_id>")
def viewer(rater_id):

    engine = get_engine()

    with engine.connect() as conn:

        # rater_uid 찾기
        rater = conn.execute(
            sqlalchemy.text("""
                SELECT rater_uid
                FROM raterDB
                WHERE rater_name = :rid
            """),
            {"rid": rater_id}
        ).mappings().fetchone()

        if not rater:
            return {"error": "rater not found"}, 404

        rater_uid = rater["rater_uid"]

        rows = conn.execute(
            sqlalchemy.text("""
                WITH latest_rater AS (
                    SELECT *
                    FROM rater_scoreDB r
                    WHERE created_at = (
                        SELECT MAX(created_at)
                        FROM rater_scoreDB
                        WHERE student_uid = r.student_uid
                        AND rater_uid = r.rater_uid
                    )
                ),

                latest_ai AS (
                    SELECT *
                    FROM ai_scoreDB a
                    WHERE created_at = (
                        SELECT MAX(created_at)
                        FROM ai_scoreDB
                        WHERE student_uid = a.student_uid
                        AND rater_uid = a.rater_uid
                    )
                ),

                latest_final AS (
                    SELECT *
                    FROM final_scoreDB f
                    WHERE created_at = (
                        SELECT MAX(created_at)
                        FROM final_scoreDB
                        WHERE student_uid = f.student_uid
                        AND rater_uid = f.rater_uid
                    )
                )

                SELECT
                    s.student_id,

                    r.knw_score AS rater_knw_score,
                    r.crt_score AS rater_crt_score,

                    a.knw_score AS ai_knw_score,
                    a.crt_score AS ai_crt_score,
                    a.knw_text,
                    a.crt_text,

                    f.knw_score AS final_knw_score,
                    f.crt_score AS final_crt_score

                FROM latest_rater r

                JOIN studentDB s
                    ON r.student_uid = s.student_uid

                LEFT JOIN latest_ai a
                    ON r.student_uid = a.student_uid
                    AND r.rater_uid = a.rater_uid

                LEFT JOIN latest_final f
                    ON r.student_uid = f.student_uid
                    AND r.rater_uid = f.rater_uid

                WHERE r.rater_uid = :uid
            """),
            {"uid": rater_uid}
        ).mappings().fetchall()

        return {
            "rater_uid": rater_uid,
            "results": [dict(row) for row in rows]
        }

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