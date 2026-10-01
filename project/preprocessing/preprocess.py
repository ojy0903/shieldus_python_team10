# 2. MongoDB 원본에서 중복 제거·마스킹 후 DataFrame으로 반환한다.
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

# True로 바꾸면 URL 하나하나의 처리 결과까지 출력 (행이 많으면 매우 길어짐)
DEBUG = False

# 팀에서 정한 접속 정보로 맞추기 (config.py가 있으면 거기서 import 해도 됨)
client = MongoClient("mongodb://localhost:27017")        # 'mongodb://localhost:27017'
db = client['url_db']                  # 'url_db'
col = db['c']              # 함수 인자로 받은 값
doc = col.find_one({"_id": ObjectId('6abe513f1651f1469d220455')})

IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
COLUMNS = ["date", "month", "masked_url", "domain", "tld"]
# CSV_NAME = "20231231.csv"  # 테스트용 CSV 파일명


# def load_csv(filename=CSV_NAME):
#     """[테스트용 //// 같은 폴더의 CSV를 읽어 MongoDB items와 같은 형태(date, url)로 반환"""
#     path = Path(__file__).parent / filename
#     if DEBUG:
#         print(f"  [DEBUG][load_csv] 시작: {path}")
#     for enc in ("utf-8-sig", "cp949"):
#         try:
#             df = pd.read_csv(path, encoding=enc)
#             break
#         except UnicodeDecodeError:
#             if DEBUG:
#                 print(f"  [DEBUG][load_csv] {enc} 인코딩 실패, 다음 인코딩 시도")
#             continue
#     print(f"[*][load_csv] CSV 로드: {path.name} ({enc}), {len(df)}건, 컬럼: {list(df.columns)}")
#     return df.rename(columns={"날짜": "date", "홈페이지주소": "url"})


# ---------- URL 하나를 처리하는 작은 함수들 ----------
# 행마다 호출되므로 DEBUG = True 일 때만 출력

def normalize_url(url):
    """ 앞뒤 공백 제거, 소문자 변환, 끝의 / 제거"""
    result = str(url).strip().lower().rstrip("/")
    if DEBUG:
        print(f"  [DEBUG][normalize_url] {url!r} -> {result!r}")
    return result


def extract_domain(url):
    """ URL에서 도메인만 추출 -> (http:// 없는 URL도 처리)"""
    target = url if "://" in url else "http://" + url
    result = urlparse(target).hostname or ""
    if not result:
        print(f"[!][extract_domain] 도메인 추출 실패 {url!r}")
    if DEBUG:
        print(f"  [DEBUG][extract_domain] {url!r} -> {result!r}")
    return result


def extract_tld(domain):
    """ 도메인 끝부분 추출, IP 주소면 'IP'"""
    if IP_PATTERN.match(domain):
        result = "IP"
    elif "." not in domain:
        result = ""
    else:
        result = domain.rsplit(".", 1)[-1]
    if DEBUG:
        print(f"  [DEBUG][extract_tld] {domain!r} -> {result!r}")
    return result


def mask_url(url):
    """ URL 마스킹 // 피해방지 : http → hxxp, . → [.]"""
    result = re.sub(r"^http", "hxxp", url).replace(".", "[.]")
    if DEBUG:
        print(f"  [DEBUG][mask_url] {url!r} -> {result!r}")
    return result


def parse_dates(series):
    """ 문자열 날짜를 datetime으로 변환 """
    try:
        result = pd.to_datetime(series, errors="coerce", format="mixed")
    except (TypeError, ValueError):  # pandas 2.0 미만 대응
        result = pd.to_datetime(series, errors="coerce")
    failed = int(result.isna().sum())
    if failed:
        print(f"[!][parse_dates] 날짜 변환 실패 {failed}건 ")
    if DEBUG:
        print(f"  [DEBUG][parse_dates] {len(result)}건 변환 완료")
    return result


# ---------- 여기부터 메인 함수 ---------------------------------------------------

def preprocess(collection_name, mongo_id):
    """MongoDB에서 원본을 읽어 중복 제거·마스킹 후 DataFrame으로 반환한다.

    Args:
        collection_name (str): 수집 데이터가 저장된 컬렉션명
        mongo_id (str): 수집 시 반환된 몽고DB ID

    Returns:
        pd.DataFrame: 전처리된 데이터 (date, month, masked_url, domain, tld)
    """
    print(f"시작: db={'url_db'}, collection={collection_name}, id={mongo_id}")

    # 1. MongoDB에서 원본 꺼내기
    try:
        object_id = ObjectId(mongo_id)
    except (InvalidId, TypeError):
        print(f"[!!][preprocess] 잘못된 mongo_id: {mongo_id!r}")
        return pd.DataFrame(columns=COLUMNS)

    client = MongoClient("mongodb://localhost:27017")
    try:
        doc = client['url_db'][collection_name].find_one({"_id": object_id})
    finally:
        client.close()

    if not doc or not doc.get("items"):
        print(f"[!!][preprocess] 문서를 찾을 수 없거나 items가 비어 있음: {mongo_id}")
        return pd.DataFrame(columns=COLUMNS)

    df = pd.DataFrame(doc["items"])
    print(f"원본: {len(df)}건 (fetched_at={doc.get('fetched_at')})")


if __name__ == "__main__":
    # 실제 컬렉션명과 수집 시 받은 _id로 바꿔서 테스트
    result = preprocess("phishing_raw", "6abe513f1651f1469d220455")
