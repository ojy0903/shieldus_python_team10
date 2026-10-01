# 4. 통계를 바탕으로 차트 이미지를 생성해 static/charts에 저장한다.

from pathlib import Path
import matplotlib.pyplot as plt


# charts.py 기준으로 project/static/charts 폴더 경로 설정
CHART_DIR = Path(__file__).resolve().parent.parent / "static" / "charts"

# static/charts 폴더가 없으면 자동 생성
CHART_DIR.mkdir(parents=True, exist_ok=True)


def save_domain_chart(stats):
    """
    TLD별 통계를 가로 막대그래프로 저장한다.

    Args:
        stats (pd.DataFrame):
            load_domain_stats()에서 반환된 통계 데이터
            예상 컬럼: tld, count

    Returns:
        str:
            저장된 이미지 파일명
    """

    # 건수가 많은 순서로 정렬한 뒤 상위 10개만 사용
    top10 = stats.sort_values(
        "count",
        ascending=False
    ).head(10)

    # 그래프 크기 설정
    plt.figure(figsize=(9, 6))

    # 가로 막대그래프 생성
    plt.barh(
        top10["tld"],
        top10["count"]
    )

    # 그래프 제목 / 축 이름
    plt.title("Phishing URL TLD TOP 10")
    plt.xlabel("Count")
    plt.ylabel("TLD")

    # 가장 많은 TLD가 위쪽에 나오도록 순서 뒤집기
    plt.gca().invert_yaxis()

    # 글자 잘림 방지
    plt.tight_layout()

    # 저장할 파일명 및 경로
    filename = "domain_chart.png"
    save_path = CHART_DIR / filename

    # 그래프 이미지 저장
    plt.savefig(save_path)

    # 메모리 정리
    plt.close()

    return filename


def save_protocol_chart(stats):
    """
    HTTP / HTTPS 통계를 막대그래프로 저장한다.

    Args:
        stats (pd.DataFrame):
            load_protocol_stats()에서 반환된 통계 데이터
            예상 컬럼: protocol, count

    Returns:
        str:
            저장된 이미지 파일명
    """

    # 그래프 크기 설정
    plt.figure(figsize=(6, 5))

    # 막대그래프 생성
    plt.bar(
        stats["protocol"],
        stats["count"]
    )

    # 그래프 제목 / 축 이름
    plt.title("HTTP / HTTPS Distribution")
    plt.xlabel("Protocol")
    plt.ylabel("Count")

    # 글자 잘림 방지
    plt.tight_layout()

    # 저장할 파일명 및 경로
    filename = "protocol_chart.png"
    save_path = CHART_DIR / filename

    # 그래프 이미지 저장
    plt.savefig(save_path)

    # 메모리 정리
    plt.close()

    return filename


# ------------------------------------------------------------
# ------------------------------------------------------------
# 아래 코드는 실제 프로젝트 실행용이 아니라,
# 시각화 함수가 정상적으로 동작하는지 확인하기 위한 테스트 코드입니다.
#
# 현재는 임시 데이터로 테스트하기 위해 주석 처리해 두었습니다.
# 실제 통계 데이터 연동 후에는 load_domain_stats(),
# load_protocol_stats() 결과를 사용하여 위 함수를 호출할 예정입니다.
# ------------------------------------------------------------
# ------------------------------------------------------------

# if __name__ == "__main__":
#     import pandas as pd
#
#     # 임시 TLD 통계 데이터
#     domain_stats = pd.DataFrame({
#         "tld": ["pro", "ly", "com", "kr", "net"],
#         "count": [9232, 1387, 974, 949, 700]
#     })
#
#     # 임시 HTTP / HTTPS 통계 데이터
#     protocol_stats = pd.DataFrame({
#         "protocol": ["http", "https"],
#         "count": [5000, 12981]
#     })
#
#     save_domain_chart(domain_stats)
#     save_protocol_chart(protocol_stats)
#
#     print("테스트 차트 생성 완료")