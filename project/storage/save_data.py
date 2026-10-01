# 3. 전처리 결과로 통계를 계산해 CSV로 저장하고, 다시 읽어 반환한다.


def save_stats(df):
    """전처리된 데이터로 통계값을 계산해 CSV로 저장한다.

    Args:
        df (pd.DataFrame): 전처리된 데이터

    Returns:
        bool: 저장 성공 여부
    """
    pass


def load_domain_stats():
    """CSV로 저장된 .kr/.net 통계를 읽어 반환한다.

    Returns:
        pd.DataFrame: .kr/.net 통계
    """
    pass


def load_protocol_stats():
    """CSV로 저장된 http/https 통계를 읽어 반환한다.

    Returns:
        pd.DataFrame: http/https 통계
    """
    pass
