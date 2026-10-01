# 1. requests로 공공데이터를 수집해 MongoDB에 저장한다.
import os
from datetime import datetime

import requests
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# MongoDB 컬렉션명(테이블명) 
COLLECTION_NAME = "phishing_url_raw"
# 공공데이터 API 에서 1페이지당 1000개의 피싱 사이트 URL 을 요청
PER_PAGE = 1000

def fetch_and_save():
    """공공데이터 API를 호출해 원본 데이터를 MongoDB에 저장한다.

    ID 값 하나로 반환하기 위해 수집 1회 분량 전체를 document 하나로 저장.
    각각의 피싱사이트 URL 과 날짜는 MongoDB ID 를 통해 document 조회한 뒤,
    "items" 키값 내부에 들어있는 리스트에서 dictionary 를 조회하여 사용

        {
            "_id": ObjectId,           # 반환되는 몽고DB ID
            "fetched_at": datetime,    # 수집 시각 
            "total_count": int,        # items 총 갯수
            "items": [                 # 피싱사이트 목록
                {"date": str, "url": str},
                ...
            ],
        }

        - date: API 에서의 날짜 값 (ex. 2023-01-01)
        - url: API 에서의 홈페이지주소 값

    Returns:
        tuple[str, str]: (컬렉션명, 몽고DB ID)
    """

    # 공공데이터 포털의 API URL 과 토큰 값 추출
    url = os.getenv("PUBLIC_DATA_URL")
    token = os.getenv("PUBLIC_DATA_TOKEN")

    # 저장될 document 내부 url, 날짜 값을 List 내부 Dictionary 로 저장
    items = []
    page = 1

    # 공공데이터 포털에서 제공하는 URL 데이터를 모두 가져올때까지 반복
    while True:
        response = requests.get(
            url,
            params = {
                "page" : page, 
                "perPage" : PER_PAGE, 
                "serviceKey": token
            },
            timeout=10
        )

        response.raise_for_status()

        body = response.json()

        # 받아온 JSON 에서 "data" 키값 내부에 있는 날짜, url 값 추출, items 에 저장
        for row in body["data"]:
            items.append({
                "date" : row["날짜"],
                "url" : row["홈페이지주소"]
            })

        # 받아온 JSON 에서 data 값이 비어있거나, 받아온 url 갯수가 totalCount 와 같으면 중단
        if not body["data"] or len(items) >= body["totalCount"]:
            break

        page += 1

    # MongoDB 세팅 : .env 내부 MongoDB 관련 값 사용
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client[os.getenv("MONGO_DB_NAME")][COLLECTION_NAME]

    # url 과 날짜가 들어있는 items 리스트, 총 갯수, 데이터 수집 날짜를 MongoDB 에 저장
    result = collection.insert_one(
        {
            "fetched_at": datetime.now().replace(microsecond=0),
            "total_count": len(items),
            "items": items,
        }
    )

    # MongoDB 연결 종료
    client.close()

    # 컬렉션명과 document id 값 반환
    return COLLECTION_NAME, str(result.inserted_id)
    

# 로컬 테스팅용 코드
if __name__ == "__main__" :
    result_tuple = fetch_and_save()
    print(f"컬렉션명: {result_tuple[0]}")
    print(f"몽고DB ID: {result_tuple[1]}")
    
    # 반환된 몽고DB ID 로 저장된 문서 조회하여 확인
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client[os.getenv("MONGO_DB_NAME")][result_tuple[0]]
    doc = collection.find_one({"_id" : ObjectId(result_tuple[1])})
    client.close()

    print(f"수집 시각: {doc['fetched_at']}")
    print(f"전체 건수: {doc['total_count']}")
    # 날짜, url 은 5건만 출력
    for item in doc["items"][0:5]:
        print(f"{item['date']} | {item['url']}")
