import streamlit as st
import google.generativeai as genai
import requests
import os
from PIL import Image
from io import BytesIO

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
        # Конфигуриране на Gemini
        genai.configure(api_key=api_key)
        # Използваме модел, който поддържа визия
        model = genai.GenerativeModel('gemini-1.5-flash')
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

    # Функция за изтегляне и конвертиране на изображение за Gemini inline format
    def load_image_for_gemini(url):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Конвертираме bytes в PIL Image за валидация
                img = Image.open(BytesIO(response.content))
                # Връщаме bytes данните - Gemini работи директно с тях
                return response.content
        except Exception as e:
            st.warning(f"Грешка при зареждане на изображение от {url}: {str(e)}")
            return None
        return None

    # Бутон за стартиране на анализа
    st.divider()
    if st.button("🚀 Стартирай ICT Анализ", type="primary"):
        if not daily_url or not h4_url or not h1_url:
            st.error("❌ Моля, попълнете линковете и за трите таймфрейма!")
        else:
            with st.spinner("🤖 Gemini агентът анализира структурата и ликвидността... Моля, изчакайте."):
                
                # Зареждане на трите изображения като bytes
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
                        # Правилният начин за подаване на изображения в google.generativeai
                        # Създаваме списък от части - текст + изображения
                        contents = [
                            prompt,
                            genai.upload_file_from_bytes(img_daily, mime_type="image/png"),
                            genai.upload_file_from_bytes(img_h4, mime_type="image/png"),
                            genai.upload_file_from_bytes(img_h1, mime_type="image/png")
                        ]
                        
                        # Извикване на модела
                        response = model.generate_content(contents)
                        
                        # Показване на резултата
                        st.success("✅ Анализът е завършен успешно!")
                        st.markdown("### 📊 Доклад от Gemini Агента")
                        st.info(response.text)
                        
                    except AttributeError:
                        # Ако upload_file_from_bytes не работи, използваме алтернативен метод
                        st.warning("Използвам алтернативен метод за прехвърляне на изображения...")
                        try:
                            # Алтернативен метод: директно подаване на bytes в списък
                            contents = [
                                prompt,
                                {"mime_type": "image/png", "data": img_daily},
                                {"mime_type": "image/png", "data": img_h4},
                                {"mime_type": "image/png", "data": img_h1}
                            ]
                            response = model.generate_content(contents)
                            st.success("✅ Анализът е завършен успешно!")
                            st.markdown("### 📊 Доклад от Gemini Агента")
                            st.info(response.text)
                        except Exception as e2:
                            st.error(f"Грешка и при алтернативния метод: {str(e2)}")
                            
                    except Exception as e:
                        st.error(f"Грешка при комуникацията с Gemini API: {str(e)}")
