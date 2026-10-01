# MongoDB에서 원본 데이터를 꺼내서 중복 제거 // 링크 마스킹 처리 등의 전처리
import pandas as p # p로 정의
import pymongo
from pymongo import MongoClient

import os
import re
from urllib.parse import urlparse



client = pymongo.MongoClient('"mongodb://localhost:27017"')
DB = os.getenv("MONGO_DB", "phishing")

IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
COLUMNS = ["date", "month", "masked_url", "domain", "tld"] # 컬럼명 

p.read_csv = (read_csv := p.read_csv)
dir(read_csv)


def preprocess(collection_name, mongo_id):
    """MongoDB에서 원본을 읽어 중복 제거·마스킹 후 DataFrame으로 반환한다.

    Args:
        collection_name (str): 수집 데이터가 저장된 컬렉션명
        mongo_id (str): 수집 시 반환된 몽고DB ID

    Returns:
        pd.DataFrame: 전처리된 데이터
    """
    pass
