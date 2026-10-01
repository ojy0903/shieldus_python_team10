# app.py — 단계별 페이지를 보여주는 Flask 서버
from flask import Flask, render_template, request, redirect, url_for

from collector.fetch_api import fetch_and_save

app = Flask(__name__)

# 각 단계 결과를 저장하는 전역변수 (아직 데이터가 없으면 None / 빈 리스트)
# 1. 수집 결과
collection_name = None
mongo_id = None
# 2. 전처리 결과
processed_data = []
# 3. CSV 저장 & 통계 결과
domain_stats = []
protocol_stats = []
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
def preprocess():
    return render_template('preprocess.html', mongo_id=mongo_id, processed_data=processed_data)

@app.route('/preprocess/run', methods=['POST'])
def run_preprocess():
    # TODO: preprocess(collection_name, mongo_id) 호출 후 processed_data 전역변수에 저장
    return redirect(url_for('preprocess'))


# 3. 전처리 데이터 → CSV 저장 & 반환
@app.route('/export')
def export():
    return render_template('export.html', processed_data=processed_data,
                           domain_stats=domain_stats, protocol_stats=protocol_stats)

@app.route('/export/run', methods=['POST'])
def run_export():
    # TODO: save_stats() 후 load_domain_stats(), load_protocol_stats() 결과를 전역변수에 저장
    return redirect(url_for('export'))


# 4. 시각화
@app.route('/visualize')
def visualize():
    return render_template('visualize.html', domain_stats=domain_stats,
                           domain_chart=domain_chart, protocol_chart=protocol_chart)

@app.route('/visualize/run', methods=['POST'])
def run_visualize():
    # TODO: save_domain_chart(), save_protocol_chart() 결과 경로를 전역변수에 저장
    return redirect(url_for('visualize'))


# 개발시 python 실행가능하도록
if __name__ == "__main__":
    app.run(debug=True)
