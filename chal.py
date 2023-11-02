import random
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def main():
    st.title("Trillion Union 카운팅🏅")

    # CSV 파일 업로드
    uploaded_file = st.file_uploader("카카오톡에서 받은 TXT 파일을 업로드하세요.", type=["csv"])

    messages = []

    import pandas as pd
import re
from google.colab import files

def process_kakao_chat_to_ranking(input_txt_content):
    # Regular expressions to match date and message patterns
    date_pattern = re.compile(r"--------------- (\d{4}년 \d{1,2}월 \d{1,2}일) .* ---------------")
    message_pattern = re.compile(r"\[(.*?)\] \[(오전|오후) (\d{1,2}:\d{2})\] (.*)")

    # Split the content into lines
    lines = input_txt_content.split('\n')

    # Extract data from the txt content
    current_date = None
    data = []
    for line in lines:
        date_match = date_pattern.match(line)
        if date_match:
            current_date = date_match.group(1)
            continue
        message_match = message_pattern.match(line)
        if message_match and current_date:
            name = message_match.group(1)
            period = message_match.group(2)
            time = message_match.group(3)
            content = message_match.group(4)
            hour, minute = map(int, time.split(':'))
            if period == "오후" and hour != 12:
                hour += 12
            formatted_time = f"{hour:02}:{minute:02}"
            data.append([name, current_date, formatted_time, content])

    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=['이름', '날짜', '시간', '내용'])
    df['날짜'] = df['날짜'].apply(lambda x: '/'.join(x.split(' ')[1:3]).replace('월', '').replace('일', ''))
    
    # Filter messages and create the ranking table
    auth_df = df[df['내용'].str.contains('인증')]
    total_auth_count = auth_df.groupby('이름').size().reset_index(name='총합')
    total_auth_count['순위'] = total_auth_count['총합'].rank(ascending=False, method='min').astype(int)
    daily_auth_count = auth_df.groupby(['이름', '날짜']).size().reset_index(name='날짜별 인증 횟수')
    pivot_df = daily_auth_count.pivot(index='이름', columns='날짜', values='날짜별 인증 횟수')
    merged_df = pd.merge(total_auth_count, pivot_df, on='이름', how='left')
    merged_df.fillna(0, inplace=True)
    # Convert the floating point numbers to integers
    for column in merged_df.columns[2:]:
        merged_df[column] = merged_df[column].astype(int)
    sorted_df = merged_df.sort_values(by='순위')
    
    return sorted_df

# Upload the TXT file
uploaded = files.upload()
for file_name in uploaded.keys():
    content = uploaded[file_name].decode('utf-8')
    result_df = process_kakao_chat_to_ranking(content)
    # Save the result as CSV
    output_csv_path = 'result.csv'
    result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    # Download the CSV file
    files.download(output_csv_path)
if __name__ == "__main__":
    main()
