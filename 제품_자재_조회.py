import pandas as pd
import streamlit as st
import gspread
from 제품_자재_조회_함수 import get_Month, get_Year, get_Mdata, data_I_search, data_M_search

credentials = st.secrets["gcp_service_account"]

st.title('제품 정보 조회 (2018/06 ~)')
''
serial_input = st.text_input("시리얼 번호를 입력하세요:", "")
''

# Google Sheets 연결 (서비스 계정 키 필요)
gc = gspread.service_account(filename="service_account.json")


if st.button("조회하기") and serial_input:
    try:
        df, df2 = get_Mdata(serial_input, gc)

        #시리얼 검색
        if serial_input not in df['SerialNo'].values:
            st.error("❌ 해당 시리얼이 존재하지 않습니다.")
        else:
            i_num, conf_N, site = data_I_search(df, serial_input)
            # 기본 정보 출력
            st.subheader("제품 기본 정보")
            st.write(f"**제품명:** {conf_N}")
            st.write(f"**사이트:** {site}")
            st.write(f"**생산년월:** {get_Year(serial_input)}년 {get_Month(serial_input)}월")

            f_df = data_M_search(df2, i_num)

            st.write(f_df)

    except Exception as e:
        st.error(f"에러 발생: {e}")
