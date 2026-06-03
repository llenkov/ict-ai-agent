import streamlit as st
from openai import OpenAI
import os

# Настройка на страницата
st.set_page_config(page_title="ICT Forex Bias Agent", page_icon="📈", layout="wide")

st.title("📈 ICT Multi-Timeframe Bias Agent")
st.markdown("Този агент анализира Forex графики на база **ICT концепциите** (Daily, 4H, 1H) и определя пазарната посока (Bias).")

# Инициализиране на OpenAI клиента
# Приложението ще търси OPENAI_API_KEY в системните променливи
api_key = os.environ.get("OPENAI_API_KEY")

# Странична лента за API ключ (ако не е зададен в системата)
if not api_key:
    api_key = st.sidebar.text_input("Въведи своя OpenAI API Key:", type="password")

if not api_key:
    st.warning("⚠️ Моля, въведете вашия OpenAI API Key в страничната лента, за да стартирате приложението.")
else:
    client = OpenAI(api_key=api_key)

    # Създаване на три колони за линковете
    st.subheader("🔗 Връзки към графиките от TradingView")
    col1, col2, col3 = st.columns(3)

    with col1:
        daily_url = st.text_input("Daily Chart URL", placeholder="https://s3.tradingview.com/...")
        if daily_url:
            st.image(daily_url, caption="Дневна графика (HTF)", use_container_width=True)

    with col2:
        h4_url = st.text_input("4H Chart URL", placeholder="https://s3.tradingview.com/...")
        if h4_url:
            st.image(h4_url, caption="4 Часа графика (MTF)", use_container_width=True)

    with col3:
        h1_url = st.text_input("1H Chart URL", placeholder="https://s3.tradingview.com/...")
        if h1_url:
            st.image(h1_url, caption="1 Час графика (LTF)", use_container_width=True)

    # Бутон за стартиране на анализа
    st.divider()
    if st.button("🚀 Стартирай ICT Анализ", type="primary"):
        if not daily_url or not h4_url or not h1_url:
            st.error("❌ Моля, попълнете линковете и за трите таймфрейма!")
        else:
            with st.spinner("🤖 Агентът анализира структурата и ликвидността... Моля, изчакайте."):
                
                system_instruction = (
                    "You are an expert Forex trader specializing in ICT (Inner Circle Trader) concepts. "
                    "Your task is to perform a multi-timeframe analysis to determine the daily BIAS (Bullish/Bearish/Neutral). "
                    "Analyze the provided chart images strictly using ICT principles: Market Structure Shift (MSS), "
                    "Fair Value Gaps (FVG), Liquidity Pools (Buy-side/Sell-side liquidity), Order Blocks (OB), and Premium/Discount arrays."
                )
                
                user_prompt = (
                    "Analyze these 3 charts from TradingView for the same currency pair:\n"
                    "1. Daily Chart: Identify the HTF narrative, major liquidity drawn, and overall Order Flow.\n"
                    "2. 4H Chart: Look for Market Structure Shifts and key Premium/Discount zones.\n"
                    "3. 1H Chart: Determine the immediate daily Bias and institutional direction.\n\n"
                    "Provide a structured output in Bulgarian language. Use professional trading terminology (can keep terms like FVG, MSS, Order Block in English or transliterated if appropriate):\n"
                    "- **Контекст от Дневна Графика (Daily)**\n"
                    "- **Структура на 4 Часа (4H)**\n"
                    "- **Посока на Влизане на 1 Час (1H)**\n"
                    "- **Крайна присъда за Дневния BIAS** (BULLISH / BEARISH / NEUTRAL) в голям, ясен формат с кратко резюме."
                )

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_prompt},
                                    {"type": "image_url", "image_url": {"url": daily_url}},
                                    {"type": "image_url", "image_url": {"url": h4_url}},
                                    {"type": "image_url", "image_url": {"url": h1_url}},
                                ],
                            }
                        ],
                        max_tokens=1200,
                        temperature=0.2
                    )
                    
                    analysis_result = response.choices[0].message.content
                    
                    # Показване на резултата в красива кутия
                    st.success("✅ Анализът е завършен успешно!")
                    st.markdown("### 📊 Доклад от AI Агента")
                    st.info(analysis_result)
                    
                except Exception as e:
                    st.error(f"Грешка при комуникацията с OpenAI: {str(e)}")