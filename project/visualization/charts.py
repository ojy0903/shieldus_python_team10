# 4. 통계를 바탕으로 차트 이미지를 생성해 static/charts에 저장한다.

from pathlib import Path
import matplotlib.pyplot as plt


CHART_DIR = Path(__file__).resolve().parent.parent / "static" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


def save_domain_chart(stats):
    """
    TLD별 통계를 가로 막대그래프로 저장한다.

    Args:
        stats (pd.DataFrame):
            check_tld_num() 결과
            예상 컬럼: tld, count

    Returns:
        str:
            저장된 이미지 파일명
    """

    top10 = stats.sort_values(
        "count",
        ascending=False
    ).head(10)

    plt.figure(figsize=(9, 6))

    plt.barh(
        top10["tld"],
        top10["count"]
    )

    plt.title("Phishing URL TLD TOP 10")
    plt.xlabel("Count")
    plt.ylabel("TLD")

    plt.gca().invert_yaxis()

    plt.tight_layout()

    filename = "domain_chart.png"
    save_path = CHART_DIR / filename

    plt.savefig(save_path)
    plt.close()

    return filename


def save_protocol_chart(stats):
    """
    HTTP / HTTPS 통계를 막대그래프로 저장한다.

    Args:
        stats (pd.DataFrame):
            check_https_http() 결과
            예상 컬럼: https, http

    Returns:
        str:
            저장된 이미지 파일명
    """

    https_count = int(stats["https"].sum())
    http_count = int(stats["http"].sum())

    protocol = ["https", "http"]
    count = [https_count, http_count]

    plt.figure(figsize=(6, 5))

    plt.bar(protocol, count)

    plt.title("HTTP / HTTPS Distribution")
    plt.xlabel("Protocol")
    plt.ylabel("Count")

    plt.tight_layout()

    filename = "protocol_chart.png"
    save_path = CHART_DIR / filename

    plt.savefig(save_path)
    plt.close()

    return filename


# ------------------------------------------------------------
# 실제 데이터 연결 테스트
# ------------------------------------------------------------

# if __name__ == "__main__":

#     # 전처리 담당 함수
#     from project.preprocessing.preprocess import preprocess

#     # 저장 / 통계 담당 함수
#     from project.storage.save_data import (
#         check_tld_num,
#         check_https_http
#     )

#     # MongoDB의 실제 피싱 URL 데이터를 전처리
#     processed_df = preprocess(
#         "phishing_raw",
#         "여기에_실제_mongo_id"
#     )

#     # 전처리 결과가 비어있는지 확인
#     if processed_df.empty:
#         print("전처리 데이터가 없습니다.")

#     else:
#         # TLD별 개수 계산
#         domain_stats = check_tld_num(processed_df)

#         # HTTP / HTTPS 여부 컬럼 생성
#         protocol_stats = check_https_http(
#             processed_df.copy()
#         )

#         # 실제 데이터로 차트 생성
#         domain_filename = save_domain_chart(
#             domain_stats
#         )

#         protocol_filename = save_protocol_chart(
#             protocol_stats
#         )

#         print("차트 생성 완료")
#         print(f"TLD 차트: {CHART_DIR / domain_filename}")
#         print(f"HTTP/HTTPS 차트: {CHART_DIR / protocol_filename}")