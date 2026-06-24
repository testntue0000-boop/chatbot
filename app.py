import os
import streamlit as st
from openai import OpenAI

# 1. 網頁基本設定 (必須放在程式碼第一行)
st.set_page_config(page_title="國北教教務處數位助理", page_icon="🎓", layout="centered")

# 2. 初始化 OpenAI 客戶端 (從環境變數讀取金鑰)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. 讀取教務處 Q&A 知識庫
def get_knowledge():
    with open("office_info.txt", "r", encoding="utf-8") as f:
        return f.read()

# 4. 網頁標題與介面設計
st.title("🎓 國立臺北教育大學")
st.subheader("教務處數位校園助理 (最終優化版)")
st.caption("歡迎使用！我是您的數位助理，精通教務處最新編制、分機、114教務會議新制法規、114碩士班考古題型，並支援周邊系統官方超連結引導。")

# 5. 初始化對話紀錄 (st.session_state 確保上下文歷史記憶)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. 渲染歷史對話到網頁上
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. 接收使用者輸入
if user_input := st.chat_input("請輸入您的校務、選課、招生考科、在學證明或學生證掛失問題..."):
    
    # 顯示使用者的問題
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 讀取權威知識庫檔案
    try:
        knowledge = get_knowledge()
    except Exception as e:
        st.error("系統錯誤：找不到知識庫檔案 office_info.txt")
        st.stop()

    # 設定系統 Prompt 角色 (降低溫度至 0.1 杜絕幻想，並強調整體解決方案提供)
    system_prompt = (
        "你現在是『國立臺北教育大學 (NTUE) 教務處數位校園助理』。請嚴格根據提供之官方 Q&A 暨職員組織權威知識庫回答問題。\n\n"
        "【回覆原則】：\n"
        "1. 語氣必須親切、客氣且極具校方專業度。以繁體中文回答。\n"
        "2. 當問題涉及到特定的行政業務時（例如：成績單核發、學歷驗證、學雜費減免、在學證明申請等），你必須在回答中【完整提供承辦人姓名、辦公室地點(室號)、分機號碼以及專門電子信箱】，絕對不可精簡。\n"
        "3. 當同學詢問『在學證明』時，你必須【同時、詳細列出免費的方案 A（學生證影印蓋章）與付費的方案 B（自動繳費機列印）兩種流程】，讓同學可以全面評估並自由選擇最適合的方案。\n"
        "4. 當提到 iNTUE、Moodle、校園入口網或計中時，【必須直接輸出知識庫中所寫的 Markdown 超連結網址】，讓同學在對話框中點擊即可直接跳轉官網。\n"
        "5. 當考生詢問碩士班開考科目時，除了給予科目名稱，【必須主動提供知識庫中記載的 114 學年度具體題型結構與配分細節】。\n"
        "6. 若問題在知識庫中完全找不到解答，請禮貌引導同學撥打學校總機 (02)2732-1104 轉接相關行政處室。\n"
        "7. 回答請儘量條列式，重點 scannable  scannable，字數請控制在 400 字內，精準直擊問題。\n\n"
        f"【官方 Q&A 暨職員組織權威知識庫內容】:\n{knowledge}"
    )

    # 顯示 AI 正在思考的動畫，並呼叫 OpenAI API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 正在為您精準查閱教務處最新法規與考古題型...")
        
        try:
            response = client.chat.completions.create(
                # model="gpt-4o-mini",
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages  # 帶入完整的 messages 歷史紀錄，完美支持上下文記憶
                ],
                max_tokens=700,    # 放大 Token 防止詳細的雙方案或考科結構被截斷
                temperature=0.1   # 將溫度降到最低，確保 AI 絕對誠實查找
            )
            answer = response.choices[0].message.content
            message_placeholder.markdown(answer)
            
            # 將 AI 的回答存入歷史紀錄
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            message_placeholder.markdown("❌ 系統服務繁忙或 API 金鑰異常，請稍後再試，或直接致電校內總機 (02)2732-1104。")
            print(f"OpenAI Error: {e}")
