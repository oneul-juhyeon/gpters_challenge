import random
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

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
            if messages:
                messages[-1] += '\n' + line.strip()
            
    df = pd.DataFrame({
        'Date': dates,
        'User': users,
        'Message': messages
    })
    return df

def main():
    st.title("Trillion 미션 카운팅🏅")
    st.caption("👍 트릴리온 폭풍성장 프로세스, 얼마나 잘 참여하고 있나요? 🥰")

    with st.sidebar:
        st.header("트릴리온 4주 성장 프로세스🔥")
        st.subheader("🚀 트릴리온 4주 성장 프로세스란?")
        st.caption("✔️혼자서는 불가능하다고 미뤄온 일 끝장내기 \n\n ✔️책과 사람을 통한 초고속 비즈니스 성장 \n\n✔️ 실행력 10배 끌어올리는 환경세팅, 72법칙\n")
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

    uploaded_file = st.file_uploader("카카오톡에서 받은 CSV 또는 TXT 파일을 업로드하세요.", type=["csv", "txt"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, dtype={"Message": str})
            elif uploaded_file.name.endswith('.txt'):
                file_contents = uploaded_file.getvalue().decode("utf-8")
                df = process_chat_with_formatted_date_and_seconds(file_contents)
                df['Message'] = df['Message'].astype(str)
            
            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns='Unnamed: 0')

            df = df[df['User'] != '오픈채팅봇']

            df['Date'] = pd.to_datetime(df['Date'])
            start_date = pd.to_datetime("2024-01-22")
            df = df[df['Date'] >= start_date]
            
            df['Date'] = df['Date'].dt.strftime('%m/%d')

            df['cnt'] = df['Message'].apply(lambda x: 1 if re.search(r'#독서인증', x, re.IGNORECASE) is not None else 0)

            result_df = df.groupby(['Date', 'User'])['cnt'].sum().reset_index()    

            final_result_df = result_df.pivot_table(index='User', columns='Date', values='cnt', aggfunc='sum').reset_index()

            final_result_df['총합'] = final_result_df.drop(columns='User').sum(axis=1)

            final_result_df = final_result_df.sort_values(by='총합', ascending=False)
            final_result_df['순위'] = range(1, len(final_result_df) + 1)

            column_order = ['순위', 'User', '총합'] + sorted([col for col in final_result_df.columns if col not in ['User', '총합', '순위']])
            final_result_df = final_result_df[column_order]
            final_result_df = final_result_df.fillna(0)

            yesterday = (datetime.now() - timedelta(days=1)).strftime('%m/%d')
            yesterday_messages = df[(df['Date'] == yesterday) & (df['cnt'] == 1) & (df['Message'].str.len() > 50)]
            yesterday_messages_list = yesterday_messages['Message'].tolist()
            if len(yesterday_messages_list) >= 5:
                random_selected_messages = random.sample(yesterday_messages_list, 5)
            else:
                random_selected_messages = yesterday_messages_list

            top_5_users = final_result_df.nlargest(5, '총합')['User'].tolist()
            top_users_str = ', '.join(top_5_users)

            successful_users_yesterday_str = ""
            if yesterday in final_result_df.columns:
                successful_users_yesterday = final_result_df[final_result_df[yesterday] > 0]['User'].tolist()
                if successful_users_yesterday:
                    successful_users_yesterday_str = ', '.join(successful_users_yesterday)

            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                daily_mission_button = st.button('독서인증')
            with col2:
                exercise_certification_button = st.button('숏폼인증')
            with col3:
                declaration_button = st.button('선언하기')
            with col4:
                weekly_mission_button = st.button('주간미션')

            if daily_mission_button:
                messages = []
                messages.append(f"### 🔥 독서 파워가 가장 높은 멤버는? \n지금까지 가장 인증을 많이 한 멤버는 {top_users_str}입니다. 부자 되시겠군요?")
                messages.append(f"### 💝 어제 독서인증을 성공한 멤버는?\n{yesterday}에 인증을 성공한 멤버는 {successful_users_yesterday_str}입니다. 어제도 정말 수고 하셨어요!")
                
                for message in messages:
                    st.markdown(message)
                
                st.markdown("\n\n", unsafe_allow_html=True)
                st.markdown("\n\n", unsafe_allow_html=True)
        
                st.subheader("독서 인증 전체 결과 보기")
        
                st.dataframe(final_result_df.reset_index(drop=True))
                
                st.markdown("\n\n", unsafe_allow_html=True)
                st.markdown("\n\n", unsafe_allow_html=True)
                st.markdown("\n\n", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()
