import streamlit as st
import google.generativeai as genai
import requests
import os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# ... (останалата част от кода за инициализация остава същата) ...

# Функция за извличане на истинския URL на изображението от TradingView страница
def get_tradingview_image_url(page_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(page_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Търсим img таг с data-src атрибут (използва се за лени зареждане)
            img_tag = soup.find('img', {'data-src': True})
            if img_tag and 's3.tradingview.com' in img_tag['data-src']:
                return img_tag['data-src']
            # Алтернативно търсим директен src атрибут
            img_tag = soup.find('img', src=True)
            if img_tag and 's3.tradingview.com' in img_tag['src']:
                return img_tag['src']
        return None
    except Exception as e:
        st.warning(f"Грешка при парсване на {page_url}: {str(e)}")
        return None

# Функция за зареждане на изображението (модифицирана)
def load_image_for_gemini(url):
    try:
        # Проверка дали URL е директен (съдържа s3.tradingview.com)
        if 's3.tradingview.com' in url:
            image_url = url
        else:
            # Ако не е директен, опитваме да извлечем истинския URL
            image_url = get_tradingview_image_url(url)
            if not image_url:
                return None
        
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.warning(f"Грешка при зареждане на изображение: {str(e)}")
        return None
    return None

# ... (останалата част от кода за Streamlit интерфейса остава същата) ...
