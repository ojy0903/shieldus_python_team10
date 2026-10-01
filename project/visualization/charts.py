# 4. 통계를 바탕으로 차트 이미지를 생성해 static/charts에 저장한다.


def save_domain_chart(stats):
    """.kr/.net 통계 차트를 저장한다.

    Args:
        stats (pd.DataFrame): load_domain_stats() 결과

    Returns:
        str: 저장된 이미지 파일명 (static/charts 기준)
    """
    pass


def save_protocol_chart(stats):
    """https/http 통계 차트를 저장한다.

    Args:
        stats (pd.DataFrame): load_protocol_stats() 결과

    Returns:
        str: 저장된 이미지 파일명 (static/charts 기준)
    """
    pass