import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- Streamlit 页面配置 ---
st.set_page_config(
    page_title="北京各城区天气预报 & 穿衣建议",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS实现蓝色背景
st.markdown("""
<style>
.stApp {
    background-color: #e0f2f7; /* 浅蓝色背景 */
}
.main-header {
    font-size: 3em;
    font-weight: bold;
    color: #2c3e50; /* 深蓝色 */
    text-align: center;
    margin-bottom: 20px;
}
.district-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.character-name {
    font-size: 1.5em;
    font-weight: bold;
    color: #e67e22; /* 橙色 */
}
.forecast-item {
    margin-bottom: 10px;
    padding: 10px;
    border-left: 5px solid #3498db;
    background-color: #f8f9fa;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# --- 爬取天气数据函数 ---
@st.cache_data(ttl=3600) # 缓存数据1小时，避免频繁请求
def scrape_weather_forecast(city_name, city_code):
    url = f"http://www.weather.com.cn/weather/{city_code}.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 如果请求不成功，抛出HTTPError
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        week_weather_div = soup.find('div', id='7d')
        if not week_weather_div:
            return []

        ul_element = week_weather_div.find('ul')
        if not ul_element:
            return []

        forecast_list = []
        day_count = 0
        for day_li in ul_element.find_all('li'):
            if day_count >= 5:
                break

            date_tag = day_li.find('h1')
            wea_tag = day_li.find('p', class_='wea')
            tem_tag = day_li.find('p', class_='tem')
            win_tag = day_li.find('p', class_='win')
            aqi_tag = day_li.find('p', class_='aqi')

            date = date_tag.text.strip() if date_tag else 'N/A'
            weather = wea_tag.text.strip() if wea_tag else 'N/A'
            temperature = tem_tag.text.strip() if tem_tag else 'N/A'
            wind = win_tag.text.strip() if win_tag else 'N/A'
            aqi = aqi_tag.text.strip() if aqi_tag else 'N/A'

            forecast_item = {
                'date': date,
                'weather': weather,
                'temperature': temperature,
                'wind': wind,
                'aqi': aqi
            }

            if '雨' in weather or '雪' in weather:
                forecast_item['precipitation'] = '有'
            else:
                forecast_item['precipitation'] = '无'

            forecast_item['humidity'] = 'N/A (需额外爬取)'
            forecast_item['warning'] = 'N/A (需额外爬取)'

            forecast_list.append(forecast_item)
            day_count += 1
        return forecast_list

    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {e}")
        return []
    except Exception as e:
        st.error(f"解析网页失败: {e}")
        return []

# --- 生成穿衣建议函数 ---
def get_clothing_advice(temperature_str, weather_desc):
    try:
        if '/' in temperature_str:
            temps = temperature_str.replace('℃', '').split('/')
            temp_low = int(temps[1].strip())
            temp_high = int(temps[0].strip())
            avg_temp = (temp_low + temp_high) / 2
        else:
            avg_temp = int(temperature_str.replace('℃', '').strip())
    except ValueError:
        return "温度数据解析失败，无法提供穿衣建议。"

    advice = "建议："
    if avg_temp < 5:
        advice += "天气严寒，请穿羽绒服、厚棉衣、冬大衣、戴帽子、围巾、手套等保暖衣物。"
    elif 5 <= avg_temp < 12:
        advice += "天气寒冷，请穿毛衣、加绒卫衣、夹克、厚外套，内搭保暖衣。"
    elif 12 <= avg_temp < 18:
        advice += "天气较凉，请穿薄毛衣、卫衣、风衣、牛仔外套、薄外套等，注意早晚温差。"
    elif 18 <= avg_temp < 25:
        advice += "天气舒适，适合穿衬衫、T恤、薄外套、休闲服。"
    else:
        advice += "天气炎热，请穿短袖、短裤、裙子等清凉透气的衣物，注意防晒。"

    if '雨' in weather_desc or '雪' in weather_desc:
        advice += " 今日有降水，出门请携带雨具，并注意防滑。"

    return advice

# --- 定义北京主要城区及其西游记人物映射 ---
BEIJING_DISTRICTS = {
    '东城区': {'code': '101010100', 'character': '唐僧', 'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/%E6%BB%A3%E5%A4%AA%E5%AD%90.png/250px-%E6%BB%A3%E5%A4%AA%E5%AD%90.png'}, # 示例URL，请替换为实际图片链接
    '西城区': {'code': '101010200', 'character': '孙悟空', 'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Monkey_King.png/250px-Monkey_King.png'},
    '朝阳区': {'code': '101010300', 'character': '猪八戒', 'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Zhu_Bajie.png/250px-Zhu_Bajie.png'},
    '海淀区': {'code': '101010400', 'character': '沙悟净', 'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Sha_Wujing.png/250px-Sha_Wujing.png'},
    '丰台区': {'code': '101010500', 'character': '白龙马', 'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Dragon_Prince_Ao_Lie.png/250px-Dragon_Prince_Ao_Lie.png'}
}

# --- Streamlit 应用主体 ---
st.markdown("<h1 class='main-header'>北京各城区天气预报与西游穿衣指南</h1>", unsafe_allow_html=True)

all_districts_weather = {}

# 使用 st.spinner 提示用户正在加载数据
with st.spinner('正在从中国天气网获取北京各城区天气数据并生成穿衣建议...'):
    for district_name, info in BEIJING_DISTRICTS.items():
        district_forecast = scrape_weather_forecast(district_name, info['code'])
        if district_forecast:
            for forecast_item in district_forecast:
                temperature = forecast_item['temperature']
                weather = forecast_item['weather']
                clothing_advice = get_clothing_advice(temperature, weather)
                forecast_item['clothing_advice'] = clothing_advice

            all_districts_weather[district_name] = {
                'character': info['character'],
                'avatar_url': info['avatar_url'],
                'forecast': district_forecast
            }
        else:
            st.warning(f"未能获取 {district_name} 的天气数据。")

if all_districts_weather:
    st.success("天气数据及穿衣建议获取完成！")
    for district_name, data in all_districts_weather.items():
        st.markdown(f"<div class='district-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 4])
        with col1:
            if data['avatar_url']:
                st.image(data['avatar_url'], caption=data['character'], width=100)
            else:
                st.write(data['character'])
        with col2:
            st.subheader(f"{district_name} ({data['character']})")

            with st.expander(f"查看 {district_name} 未来5天天气预报和穿衣建议"):
                for item in data['forecast']:
                    st.markdown(
                        f"""
                        <div class='forecast-item'>
                            📅 **日期**: {item['date']}<br>
                            ☀️ **天气**: {item['weather']}<br>
                            🌡️ **温度**: {item['temperature']}<br>
                            💧 **降水**: {item['precipitation']}<br>
                            🌬️ **风力**: {item['wind']}<br>
                            👕 **穿衣建议**: {item['clothing_advice']}
                        </div>
                        """, unsafe_allow_html=True
                    )
        st.markdown(f"</div>", unsafe_allow_html=True)
else:
    st.error("未能获取任何北京城区的天气数据，请检查网络连接或网站结构。")
