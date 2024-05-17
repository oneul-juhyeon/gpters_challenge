import random
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

# 추가된 함수: txt 파일을 csv 형식으로 변환하는 함수
def process_chat_with_formatted_date_and_seconds(file_contents):
    lines = file_contents.split('\n')
    dates = []
    users = []
    messages = []
    current_date = None

    date_pattern = re.compile(r'--------------- (\d{4}년 \d{1,2}월 \d{1,2}일) .+ ---------------')
    message_pattern = re.compile(r'\[(.+?)\] \[(오전|오후) (\d{1,2}:\d{2})\] (.+)')

    for line in lines:
        date_match = date_pattern.match(line)
        if date_match:
            current_date = date_match.group(1)
            current_date = pd.to_datetime(current_date, format='%Y년 %m월 %d일').strftime('%Y-%m-%d')
            continue

        message_match = message_pattern.match(line)
        if message_match and current_date:
            user = message_match.group(1)
            am_pm = message_match.group(2)
            time = message_match.group(3)
            message = message_match.group(4)

            # Convert Korean AM/PM to 24-hour format
            if am_pm == '오후' and time.split(':')[0] != '12':
                hour = str(int(time.split(':')[0]) + 12)
                time = hour + time[time.find(':'):]
            elif am_pm == '오전' and time.split(':')[0] == '12':
                time = '00' + time[time.find(':'):]
            
            full_datetime = f"{current_date} {time}"
            dates.append(full_datetime)
            users.append(user)
            messages.append(message)
        else:
            # If the line doesn't match the message pattern, append it to the previous message
            if messages:
                messages[-1] += '\n' + line.strip()
            
    df = pd.DataFrame({
        'Date': dates,
        'User': users,
        'Message': messages
    })
    return df

# main 함수 수정
def main():
    st.title("ME before TRILLION🌷")
    st.caption("👍 Writing is a mirror that reflects you : 인생을 바꾸기 전, 진정한 나를 마주하는 시간 🥰")

    with st.sidebar:
        st.header("ME before TRILLION🌷")

        st.subheader("✡️조만장자가 될 사람들의 모임")
        st.caption("👀트릴리온이 궁금해? : [링크](https://blog.naver.com/yoo1104/223322531413)")

        st.header("만든 사람")
        st.markdown("😄 트릴리온 커뮤니티 리더 주현영")
        st.markdown("❤️ 트릴리온 인스타 : [링크](https://www.instagram.com/trillion_union/)")
        st.markdown("📗 주현영 블로그 : [링크](https://blog.naver.com/todaygrowth)")

        st.header("도와준 사람")
        st.markdown("😍 지피터스 커뮤니티 리더 윤누리")

        st.header("열일한 노예")
        st.markdown("👽 Chat GPT")

    # CSV와 TXT 파일 업로드 지원
    uploaded_file = st.file_uploader("카카오톡에서 받은 CSV 또는 TXT 파일을 업로드하세요.", type=["csv", "txt"])

    messages = []

    if uploaded_file:
        # 파일 확장자에 따라 처리 방식 변경
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, dtype={"Message": str})
        elif uploaded_file.name.endswith('.txt'):
            # TXT 파일을 읽어서 전처리
            file_contents = uploaded_file.getvalue().decode("utf-8")
            df = process_chat_with_formatted_date_and_seconds(file_contents)
            
            # 'Message' 열의 모든 데이터를 문자열로 변환
            df['Message'] = df['Message'].astype(str)
            
        # 'Unnamed: 0' 열 제거
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns='Unnamed: 0')

        # '오픈채팅봇' 제외
        df = df[df['User'] != '오픈채팅봇']

        # 날짜 형식 변경
        start_date = pd.to_datetime("2024-01-22") # 여기서 날짜를 설정하세요
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'] >= start_date]
        df['Date'] = df['Date'].dt.strftime('%m/%d')

        # Message에서 #인증 단어가 있는지 확인하고 cnt 컬럼 생성
        df['cnt'] = df['Message'].apply(lambda x: 1 if '#인증' in str(x) else 0)

        # 어제의 메시지 중 #인증이 포함된 메시지 필터링
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%m/%d')
        yesterday_messages = df[(df['Date'] == yesterday) & (df['cnt'] == 1)]
        yesterday_messages_list = yesterday_messages['Message'].tolist()
        if len(yesterday_messages_list) >= 5:
            random_selected_messages = random.sample(yesterday_messages_list, 5)
        else:
            random_selected_messages = yesterday_messages_list

        # 날짜별로 cnt 합계 계산
        result_df = df.groupby(['Date', 'User'])['cnt'].sum().reset_index()    

        # 최종 결과 데이터프레임 생성
        final_result_df = result_df.pivot_table(index='User', columns='Date', values='cnt', aggfunc='sum').reset_index()

        # 'User' 열을 제외하고 합산
        final_result_df['총합'] = final_result_df.drop(columns='User').sum(axis=1)

        # Now that '총합' is available, you can find the top 5 users
        top_5_users = final_result_df.nlargest(5, '총합')['User'].tolist()
        top_users_str = ', '.join(top_5_users)

        # 어제 인증을 성공한 멤버 찾기
        successful_users_yesterday_str = ""
        if yesterday in final_result_df.columns:
            successful_users_yesterday = final_result_df[final_result_df[yesterday] > 0]['User'].tolist()
            if successful_users_yesterday:
                successful_users_yesterday_str = ', '.join(successful_users_yesterday)

        final_result_df = final_result_df.sort_values(by='총합', ascending=False)
        final_result_df['순위'] = range(1, len(final_result_df) + 1)

        # 컬럼 순서 조정
        column_order = ['순위', 'User', '총합'] + sorted([col for col in final_result_df.columns if col not in ['User', '총합', '순위']])
        final_result_df = final_result_df[column_order]
        final_result_df.fillna(0, inplace=True)

        # 인증 결과 표시 버튼
        certification_button = st.button('인증 결과 보기')

        # 인증 결과 표시 (index=False로 설정하여 인덱스를 표시하지 않음)
        if certification_button:
            messages.append(f"### 🔥 인증 파워가 가장 높은 멤버는? \n지금까지 가장 인증을 많이 한 멤버는 {top_users_str}입니다.")
            messages.append(f"### 💝 어제 인증을 성공한 멤버는?\n{yesterday}에 인증을 성공한 멤버는 {successful_users_yesterday_str}입니다. 어제도 정말 수고 하셨어요!")
            
            for message in messages:
                st.markdown(message)
               
            # 표와 메시지 사이의 줄바꿈 추가
            st.markdown("\n\n", unsafe_allow_html=True)
            st.markdown("\n\n", unsafe_allow_html=True)
    
            # 전체 결과 보기
            st.subheader("인증 전체 결과 보기")
    
            # 결과 표시 (index=False로 설정하여 인덱스를 표시하지 않음)
            st.dataframe(final_result_df.reset_index(drop=True))
            
            # 줄바꿈 추가
            st.markdown("\n\n", unsafe_allow_html=True)
            st.markdown("\n\n", unsafe_allow_html=True)
            st.markdown("\n\n", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
