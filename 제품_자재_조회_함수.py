import pandas as pd

# 시리얼 내용연수 확인
def get_Year(serial):
    year_prefix = '202' if int(serial[0]) < 8 else '201'
    year = year_prefix + serial[0]
    return year

def get_Month(serial):
    if serial[1].upper() == 'A':
        month = 10
    elif serial[1].upper() == 'B':
        month = 11
    elif serial[1].upper() == 'C':
        month = 12
    else: 
        month = serial[1]
    return month

# 연도별 URL
instruct_urls = {
    '2018': 'https://docs.google.com/spreadsheets/d/1g7z0l98vryzNGwq_-9HJk0D72VjQL2Ame_qWGJIgq90/edit#gid=413308200',
    '2019': 'https://docs.google.com/spreadsheets/d/19Tfy5Bv6zGMEvIbmxDc9WJ2V9lKJLJqW9F7vB6yYPEI/edit#gid=2138865825',
    '2020': 'https://docs.google.com/spreadsheets/d/10qUf7a5fI-5W6ynF6wzOQFfaFeD-F52hn-ZDmgq5eIQ/edit#gid=574038048',
    '2021': 'https://docs.google.com/spreadsheets/d/173_-fYzF2FtKK9CMgr7W6ONdCHJ8Zo-p71ZXvqlWDGQ/edit#gid=1188382345',
    '2022': 'https://docs.google.com/spreadsheets/d/1ymjxsMZlAfSTllTsNZ4FI_nsZGy1TtxmuyD0MHQKqdE/edit#gid=53146201',
    '2023': 'https://docs.google.com/spreadsheets/d/1O0Eo2FvW2MietSE969DPMEls8N1yUaLvkU9a1xwQUmg/edit#gid=1843965467',
    '2024': 'https://docs.google.com/spreadsheets/d/1ApQrhqpGKxfAcsBSB97Xp4s-Xaivp-H4sEvEmiRFf2w/edit#gid=435793914',
    '2025': 'https://docs.google.com/spreadsheets/d/1vNzadtBo0Mk3tLjm7kR0BBtMr-drEehIY6SEwSrYVpQ/edit?gid=1997354010#gid=1997354010'
}

# 데이터 불러오기
def get_Mdata(serial, gc):
    """시리얼로 데이터 불러오기"""
    year = get_Year(serial)
    doc = gc.open_by_url(instruct_urls.get(year))

    # 데이터 가져오기
    worksheet1 = doc.worksheet("바코드발행리스트")
    worksheet2 = doc.worksheet("생산투입리스트")

    data1 = worksheet1.get('A:E')
    data2 = worksheet2.get('B:I')

    df = pd.DataFrame(data1[1:], columns=data1[0])
    df2 = pd.DataFrame(data2[1:], columns=data2[0])    

    return df, df2


# 시리얼 관련 제품명,사이트, 생산일자 조회 
def data_I_search(df, serial):
    i_num = df.loc[df['SerialNo'] == serial, '작업지시번호'].iloc[0]
    conf_N = df.loc[df['SerialNo'] == serial, '품목'].iloc[0]
    site = df.loc[df['SerialNo'] == serial, 'SITE'].iloc[0]

    return i_num, conf_N, site


# 시리얼 관련 투입 자재 조회
def data_M_search(df2, i_num):
    m_df = df2[df2['지시번호'].str.contains(i_num)]
    m_df = m_df.reset_index(drop=True)

    # 투입 자재 리스트
    all_M = [[],[],[],[],[],[],[],[],[]]
    # 투입 자재 수량 리스트
    all_Mn = [[],[],[],[],[],[],[],[],[]]
    # 투입 자재 판매가 리스트
    all_Mp = [[],[],[],[],[],[],[],[],[]]
    # 투입 자재 코드 리스트
    all_Mc = [[],[],[],[],[],[],[],[],[]]
    # 메인 자재명
    all_MM = [['CPU'],['메인보드'],['스케일러'],['윈도우키'],['SSD'],['HDD'],['메모리'],['파워'],['패널']]
    # 컬럼영
    all_Ma = ['코드', '품목', '수량', '판매가']

    # 자재 분류
    categories = {
        0: ('CPU', lambda x: 'CPU' in x and 'COOLER' not in x),
        1: ('메인보드', lambda x: 'MAIN BOARD' in x or 'M/B, thin-ITX' in x),
        2: ('스케일러', lambda x: 'BYPASS' in x),
        3: ('윈도우키', lambda x: any(key in x for key in ['OPTION, ROYALTY','Home','Pro','LABEL'])),
        4: ('SSD', lambda x: 'SSD' in x),
        5: ('HDD', lambda x: 'HDD' in x and 'BRACKET' not in x),
        6: ('메모리', lambda x: 'MEMORY' in x.upper()),
        7: ('파워', lambda x: any(key in x for key in ['SMPS, TFX', 'SMPS, ATX', 'POWER, SMPS', 'POWER ATX NORMAL', 'ADAPTER', 'ADAPTOR', 'SMPS 400W TFX','SMPS'])),
        8: ('패널', lambda x: 'PANEL' in x),
    }

    for i in m_df.index:
        name = m_df.loc[i,'소요자재명']
        for idx, (label, condition) in categories.items():
            if condition(name):
                all_M[idx].append(m_df.loc[i,'소요자재규격'])
                all_Mn[idx].append(m_df.loc[i,'단위수량'])
                all_Mc[idx].append(m_df.loc[i,'시스템코드'])
                all_Mp[idx].append(m_df.loc[i,'판매가'])


    # 평탄화 

    all_M = [x[0] if x else '-' for x in all_M]
    all_Mn = [x[0] if x else '-' for x in all_Mn]
    all_Mp = [x[0] if x else '-' for x in all_Mp]
    all_Mc = [x[0] if x else '-' for x in all_Mc]
    all_MM = [x[0] if x else '-' for x in all_MM]


    df1 = pd.DataFrame(all_M, index=all_MM)
    df2 = pd.DataFrame(all_Mn, index=all_MM)
    df3 = pd.DataFrame(all_Mp, index=all_MM)
    df4 = pd.DataFrame(all_Mc, index=all_MM)

    f_df = pd.concat([df4, df1, df2, df3], axis=1)
    f_df.columns = all_Ma

    f_df = (
        f_df.style
            .set_properties(**{'text-align': 'center'})   # 데이터 값 좌측 정렬
            .set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'center')]}]  # 열 이름 가운데 정렬
            )
    )
    return f_df