# app.py — 단계별 페이지를 보여주는 Flask 서버
from flask import Flask, render_template, request, redirect, url_for

from collector.fetch_api import fetch_and_save
# 라우트 함수 preprocess() 와 이름이 겹치므로 별칭으로 import
from preprocessing.preprocess import preprocess as preprocess_data
from storage.save_data import check_https_http, check_tld_num, save_csv
import os
# Flask 는 GUI 창이 없으므로 이미지 파일 저장 전용 백엔드 사용 (charts import 전에 설정)
import matplotlib
matplotlib.use('Agg')
from visualization.charts import save_domain_chart, save_protocol_chart

app = Flask(__name__)

# CSV 저장 경로 (실행 위치와 상관없이 project/data/processed 아래에 저장)
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'processed', 'classified_phishing_data.csv')

# 각 단계 결과를 저장하는 전역변수 (아직 데이터가 없으면 None / 빈 리스트)
# 1. 수집 결과
collection_name = None
mongo_id = None
# 2. 전처리 결과 (DataFrame, 3단계 save_stats() 에 그대로 넘김)
processed_data = None
# 전처리 페이지에 미리보기로 보여줄 행 수
PREVIEW_ROWS = 20
# 3. CSV 저장 결과 (저장된 파일명)
csv_file = None
# 4. 시각화 결과 (static 기준 이미지 경로)
domain_chart = None
protocol_chart = None


# 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')


# 1. 공공데이터 수집 → MongoDB 저장
@app.route('/collect')
def collect():
    return render_template('collect.html', collection_name=collection_name, mongo_id=mongo_id)

@app.route('/collect/run', methods=['POST'])
def run_collect():
    global collection_name, mongo_id
    # 공공데이터 수집 후 MongoDB 저장, 반환된 컬렉션명과 몽고DB ID 를 전역변수에 저장
    try:
        collection_name, mongo_id = fetch_and_save()
    except Exception as e:
        # .env 미설정, API/MongoDB 통신 실패 등은 수집 페이지에 에러 메시지로 표시
        return render_template('collect.html', collection_name=collection_name,
                               mongo_id=mongo_id, error=str(e))
    return redirect(url_for('collect'))


# 2. MongoDB 원본 → 중복 제거 & 링크 마스킹
@app.route('/preprocess')
def preprocess(error=None):
    # 전체 데이터는 수만 건이라 앞부분만 dict 리스트로 바꿔 템플릿에 전달
    if processed_data is None:
        rows, total_count = [], 0
    else:
        # pandas에서 astype({'date': str})으로 JSON 직렬화
        rows = processed_data.head(PREVIEW_ROWS).astype({'date': str}).to_dict('records')
        total_count = len(processed_data)
    return render_template('preprocess.html', mongo_id=mongo_id, processed_data=rows,
                           total_count=total_count, error=error)

# 실제 전처리 수행
@app.route('/preprocess/run', methods=['POST'])
def run_preprocess():
    global processed_data
    # 1단계에서 저장한 MongoDB 문서를 전처리, 결과 DataFrame 을 전역변수에 저장
    try:
        result = preprocess_data(collection_name, mongo_id)
    except Exception as e:
        # MongoDB 접속 실패 등은 전처리 페이지에 에러 메시지로 표시
        return preprocess(error=str(e))
    # preprocess() 는 문서를 못 찾으면 예외 대신 빈 DataFrame 을 반환
    if result.empty:
        return preprocess(error='MongoDB 에서 수집 데이터를 찾지 못했습니다.')
    processed_data = result
    return redirect(url_for('preprocess'))


# 2. 전처리 데이터 → CSV 저장 & 반환
@app.route('/export')
def export():
    # DataFrame 은 템플릿 if 문에서 참/거짓 판단이 안 되므로 전처리 완료 여부만 전달
    return render_template('export.html', processed_data=processed_data is not None,
                           csv_file=csv_file)

# 3. 실제 CSV 저장 & 통계 수행
@app.route('/export/run', methods=['POST'])
def run_export():
    global csv_file
    if processed_data is None:
        return redirect(url_for('export'))
    # 원본 전역변수가 바뀌지 않도록 복사본에 http/https 열 추가
    df = check_https_http(processed_data.copy())
    # 저장에 성공하면 실제 저장된 파일명을 전역변수에 저장
    if save_csv(df, CSV_PATH):
        csv_file = os.path.basename(CSV_PATH)
    return redirect(url_for('export'))


# 4. 시각화
@app.route('/visualize')
def visualize():
    return render_template('visualize.html', csv_file=csv_file,
                           domain_chart=domain_chart, protocol_chart=protocol_chart)

# 실제 차트 생성
@app.route('/visualize/run', methods=['POST'])
def run_visualize():
    global domain_chart, protocol_chart
    if processed_data is None:
        return redirect(url_for('visualize'))
    # 전처리 데이터로 tld 개수, http/https 여부를 구해 차트 이미지 생성
    df = check_https_http(processed_data.copy())
    # charts 는 static/charts 기준 파일명을 반환하므로 static 기준 경로로 저장
    domain_chart = 'charts/' + save_domain_chart(check_tld_num(df))
    protocol_chart = 'charts/' + save_protocol_chart(df)
    return redirect(url_for('visualize'))


# 개발시 python 실행가능하도록
if __name__ == "__main__":
    app.run(debug=True)
