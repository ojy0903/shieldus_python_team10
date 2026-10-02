import pandas as pd
import os
import re



def check_https_http(df=None):
    '''
    마스킹된 url에서 http 또는 https를 포함하는지 검사하고 데이터 프레임에 여부를 저장하는 함수
    매개변수
    df : 검사할 데이터 프레임

    반환값 : http, https 열을 추가한 df(데이터프레임)

    df에 추가되는 속성
    https : https 포함여부 (bool)
    http : http 포함 여부 (bool)
    '''
    if df is None:
        print('데이터프레임을 연결해주세요.')#데이터 프레임 유무
    else:
        df["https"] = False #https 열 생성
        df["http"] = False #http 열 생성

        for i, address in enumerate(df["masked_url"]):  # 마스킹된 url 순회
            try:
                if re.search(r"hxxps?", address): #만약 hxxps 또는 hxxp를 만나면
                    if "hxxps" in address:
                        df.loc[i,"https"] = True #hxxps일 경우 https를 True로 바꾸기
                    else:
                        df.loc[i,"http"] = True #hxxp일 경우 http를 True로 바꾸기
                else:
                    # print("http/https 가 아닙니다")
                    continue
            except Exception as e: #아주 만약에 결측치를 만나는 등의 에러가 난다면 넘어가도록 에러처리
                # print(f'{i} 행{e} 에러 입니다.')
                continue
    return df

def check_tld_num(df):
    '''
    tld의 종류별로 변수를 지정해 갯수를 저장하는 함수
    매개변수
    df : 데이터프레임

    반환값 
    tld : df에 저장된 tld와 개수를 저장한 데이터프레임

    tld에 포함되어있는 속성
    tld : tdl의 종류
    count : tdl의 개수
    '''
    if df is None:
        print('데이터프레임을 연결해주세요.')#데이터 프레임 유무
    else:
        #딕셔너리 생성
        data = {}

        for t in df["tld"]: # tld 순회
            
            try:
                if pd.isna(t): #결측치 뛰어넘기
                    continue


                # {tld: count}의 형식으로 만들어짐
                if t in data: # 딕셔너리에 있으면 1 추가
                    data[t] += 1
                else: # 딕셔너리에 없으면 새로 생성 
                    data[t] = 1

            except Exception as e:
                # print(f'{i} 행{e} 에러 입니다.')
                continue
    #앞에서 만든 딕셔너리를 {"tld" : [tld 종류], "count" : [개수]} 형태로 변환 후 데이터프레임으로 저장
    tld_df = pd.DataFrame({
        "tld": list(data.keys()),
        "count": list(data.values())
    })

    return tld_df

def save_csv(df, file_path="classified_phishing_data.csv"):
    '''
    csv 파일로 저장하는 함수 
    매개변수 
    df : 데이터프레임
    file_path : 문자열, 저장할 파일 이름 또는 전체 경로 (기본값: 'classified_phishing_data.csv')
    예시: "output/classified_result.csv"

    반환값
    is_saved : csv파일로 저장됬는지 여부 (bool) 
    '''
    if df is None:
        print("데이터프레임을 연결해주세요.")#데이터프레임 유무
        return False

    if df.empty:
        print("데이터프레임이 비어 있습니다. 빈 파일이 생성될 수 있습니다.")#데이터프레임 비어있는지 확인

    try:
        # 지정한 디렉토리(폴더) 경로가 없으면 자동으로 생성
        directory = os.path.dirname(file_path) 
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # CSV 파일로 저장
        #index 없애고 한글이나 특수문자 안깨지게 처리
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return True

    #오류 처리
    except Exception as e:
        print(f"[ERROR] CSV 파일 저장 중 오류 발생: {e}")
        return False
    

        