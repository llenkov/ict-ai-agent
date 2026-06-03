import streamlit as st
import google.genai as genai
import requests
import os

# Настройка на страницата
st.set_page_config(page_title="ICT Forex Bias Agent (Gemini)", page_icon="📈", layout="wide")

st.title("📈 ICT Multi-Timeframe Bias Agent (Безплатен с Gemini)")
st.markdown("Този агент анализира Forex графики на база **ICT концепциите** (Daily, 4H, 1H) и определя пазарната посока (Bias).")

# Инициализиране на Gemini API ключа от Secrets
api_key = os.environ.get("GEMINI_API_KEY")

# Странична лента за ръчно въвеждане (ако няма такъв в Secrets)
if not api_key:
    api_key = st.sidebar.text_input("Въведи своя Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Моля, въведете вашия Gemini API Key в страничната лента, за да стартирате приложението.")
else:
    try:
        # Използваме новия, сигурен клиент на Google
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Грешка при инициализиране на клиента: {str(e)}")

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

    # Функция за изтегляне на изображението в правилния за новия SDK формат
    def load_image_for_gemini(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Новата библиотека изисква Part.from_bytes за изображения
                return genai.types.Part.from_bytes(
                    data=response.content,
                    mime_type="image/png"
                )
        except:
            return None
        return None

    # Бутон за стартиране на анализа
    st.divider()
    if st.button("🚀 Стартирай ICT Анализ", type="primary"):
        if not daily_url or not h4_url or not h1_url:
            st.error("❌ Моля, попълнете линковете и за трите таймфрейма!")
        else:
            with st.spinner("🤖 Новият Gemini агент анализира структурата и ликвидността... Моля, изчакайте."):
                
                # Зареждане на трите изображения
                img_daily = load_image_for_gemini(daily_url)
                img_h4 = load_image_for_gemini(h4_url)
                img_h1 = load_image_for_gemini(h1_url)
                
                if not img_daily or not img_h4 or not img_h1:
                    st.error("❌ Грешка при изтеглянето на изображенията. Увери се, че линковете са правилни.")
                else:
                    # Промпт с инструкции
                    prompt = (
                        "You are an expert Forex trader specializing in ICT (Inner Circle Trader) concepts. "
                        "Your task is to perform a multi-timeframe analysis to determine the daily BIAS (Bullish/Bearish/Neutral). "
                        "Analyze the 3 attached chart images (Daily, 4H, and 1H in that order) strictly using ICT principles: "
                        "Market Structure Shift (MSS), Fair Value Gaps (FVG), Liquidity Pools (Buy-side/Sell-side liquidity), "
                        "Order Blocks (OB), and Premium/Discount arrays.\n\n"
                        "Provide a structured output in Bulgarian language. Use professional trading terminology (keep terms like FVG, MSS, Order Block in English if appropriate):\n"
                        "- **Контекст от Дневна Графика (Daily)**: Identify the HTF narrative and major liquidity drawn.\n"
                        "- **Структура на 4 Часа (4H)**: Look for Market Structure Shifts and key Premium/Discount zones.\n"
                        "- **Посока на Влизане на 1 Час (1H)**: Determine immediate daily direction.\n"
                        "- **Крайна присъда за Дневния BIAS** (BULLISH / BEARISH / NEUTRAL) в голям, ясен формат с кратко резюме."
                    )

                    try:
                        # Извикване чрез новия метод на Google SDK
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[prompt, img_daily, img_h4, img_h1]
                        )
                        
                        # Показване на резултата
                        st.success("✅ Анализът е завършен успешно!")
                        st.markdown("### 📊 Доклад от Gemini Агента")
                        st.info(response.text)
                        
                    except Exception as e:
                        st.error(f"Грешка при комуникацията с Gemini API: {str(e)}")
