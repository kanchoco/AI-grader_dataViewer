import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google.cloud.sql.connector import Connector
import sqlalchemy
import pandas as pd
import uuid
from flask import send_file
import io


# React build 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_BUILD_PATH = os.path.join(os.path.dirname(BASE_DIR), "dist")

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
SQL = """ WITH base AS (
    SELECT student_uid, rater_uid
    FROM rater_scoreDB
    GROUP BY student_uid, rater_uid
),

latest_ai AS (
    SELECT *
    FROM (
        SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY student_uid, rater_uid
            ORDER BY created_at DESC
        ) AS rn
        FROM ai_scoreDB
    ) t
    WHERE rn = 1
),

latest_final AS (
    SELECT *
    FROM (
        SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY student_uid, rater_uid
            ORDER BY created_at DESC
        ) AS rn
        FROM final_scoreDB
    ) t
    WHERE rn = 1
),

latest_rater AS (
    SELECT *
    FROM (
        SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY student_uid, rater_uid
            ORDER BY created_at DESC
        ) AS rn
        FROM rater_scoreDB
    ) t
    WHERE rn = 1
)

SELECT
    rd.rater_id,
    s.student_id,

    r.knw_score AS rater_knw_score,
    r.crt_score AS rater_crt_score,

    a.knw_score AS ai_knw_score,
    a.crt_score AS ai_crt_score,
    a.knw_text,
    a.crt_text,

    f.knw_score AS final_knw_score,
    f.crt_score AS final_crt_score,

    a.created_at AS ai_time,
    f.created_at AS final_time

FROM base b

LEFT JOIN latest_rater r
ON b.student_uid = r.student_uid
AND b.rater_uid = r.rater_uid

LEFT JOIN latest_ai a
ON b.student_uid = a.student_uid
AND b.rater_uid = a.rater_uid

LEFT JOIN latest_final f
ON b.student_uid = f.student_uid
AND b.rater_uid = f.rater_uid

JOIN studentDB s
ON b.student_uid = s.student_uid

JOIN raterDB rd
ON b.rater_uid = rd.rater_uid

ORDER BY rd.rater_id, s.student_id; """

@app.get("/expert_excel")
def export_excel():

    engine = get_engine()

    with engine.connect() as conn:
        rows = conn.execute(sqlalchemy.text(SQL)).mappings().fetchall()

    df = pd.DataFrame(rows)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="scores")

    output.seek(0)

    return send_file(
        output,
        download_name="all_scores.xlsx",
        as_attachment=True
    )

@app.get("/viewer")
def viewer():

    engine = get_engine()

    with engine.connect() as conn:
        rows = conn.execute(sqlalchemy.text(SQL)).mappings().fetchall()

    return {"results": [dict(r) for r in rows]}

# 프런트엔드 서빙
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):

    if path.startswith("viewer"):
        return {"error": "not found"}, 404

    file_path = os.path.join(app.static_folder, path)

    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)

    return send_from_directory(app.static_folder, "index.html")