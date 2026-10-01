# 2. MongoDB 원본에서 중복 제거·마스킹 후 DataFrame으로 반환한다.


def preprocess(collection_name, mongo_id):
    """MongoDB에서 원본을 읽어 중복 제거·마스킹 후 DataFrame으로 반환한다.

    Args:
        collection_name (str): 수집 데이터가 저장된 컬렉션명
        mongo_id (str): 수집 시 반환된 몽고DB ID

    Returns:
        pd.DataFrame: 전처리된 데이터
    """
    pass
