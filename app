import requests
from bs4 import BeautifulSoup

def scrape_weather_forecast(city_name, city_code):
    url = f"http://www.weather.com.cn/weather/{city_code}.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # print(f"Debug: 尝试请求URL: {url}") # 可以取消注释进行调试
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 如果请求不成功，抛出HTTPError
        # print(f"Debug: 请求成功，状态码: {response.status_code}")
        # print(f"Debug: 响应URL: {response.url}")

        response.encoding = 'utf-8' # 设置正确的编码
        soup = BeautifulSoup(response.text, 'lxml')
        # print("Debug: BeautifulSoup解析成功。")

        # 找到包含7天预报的div，其id为'7d'
        week_weather_div = soup.find('div', id='7d')
        if not week_weather_div:
            # print("Debug: 未找到id为'7d'的div。网站结构可能已变更。")
            return []
        # print("Debug: 找到id为'7d'的div。")

        # 在此div内部，尝试找到第一个ul元素，不指定class
        ul_element = week_weather_div.find('ul')
        if not ul_element:
            # print("Debug: 未找到id为'7d'的div内的ul元素。")
            return []
        # print("Debug: 找到id为'7d'的div内的ul元素。")

        forecast_list = []
        day_count = 0
        # 遍历每个li元素，代表每天的预报
        for day_li in ul_element.find_all('li'):
            if day_count >= 5: # 我们只需要5天的预报
                break

            date_tag = day_li.find('h1')
            wea_tag = day_li.find('p', class_='wea')
            tem_tag = day_li.find('p', class_='tem')
            win_tag = day_li.find('p', class_='win') # 查找风力信息
            aqi_tag = day_li.find('p', class_='aqi') # 查找AQI信息

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

            # 根据天气描述判断是否有降水
            if '雨' in weather or '雪' in weather:
                forecast_item['precipitation'] = '有'
            else:
                forecast_item['precipitation'] = '无'

            # 湿度、预警等信息在5天预报列表中可能不直接显示，或需要更复杂的爬取逻辑。
            # 目前设置为占位符，如果需要，后续可以针对性地添加代码来获取。
            forecast_item['humidity'] = 'N/A (需额外爬取)'
            forecast_item['warning'] = 'N/A (需额外爬取)'

            forecast_list.append(forecast_item)
            day_count += 1

        # print(f"Debug: 成功解析 {len(forecast_list)} 天预报数据。")
        return forecast_list

    except requests.exceptions.RequestException as e:
        print(f"Error: 网络请求失败: {e}")
        return []
    except Exception as e:
        print(f"Error: 解析网页失败: {e}")
        return []

def get_clothing_advice(temperature_str, weather_desc):
    # 提取温度值，假设格式为 'XX/YY℃' 或 'XX℃'
    try:
        # 尝试匹配 'XX/YY℃' 格式，取高低温的平均值
        if '/' in temperature_str:
            temps = temperature_str.replace('℃', '').split('/')
            temp_low = int(temps[1].strip())
            temp_high = int(temps[0].strip())
            avg_temp = (temp_low + temp_high) / 2
        else:
            # 尝试匹配 'XX℃' 格式，直接取值
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

# 定义北京主要城区的城市代码和对应的西游记人物
BEIJING_DISTRICTS = {
    '东城区': {'code': '101010100', 'character': '唐僧', 'avatar_url': 'https://example.com/tangseng.png'}, # 示例URL，您需要替换为实际图片链接
    '西城区': {'code': '101010200', 'character': '孙悟空', 'avatar_url': 'https://example.com/wukong.png'},
    '朝阳区': {'code': '101010300', 'character': '猪八戒', 'avatar_url': 'https://example.com/bajie.png'},
    '海淀区': {'code': '101010400', 'character': '沙悟净', 'avatar_url': 'https://example.com/wujing.png'},
    '丰台区': {'code': '101010500', 'character': '白龙马', 'avatar_url': 'https://example.com/bailongma.png'}
}

# 获取北京各个城区的天气预报
all_districts_weather = {}

print("正在尝试从中国天气网爬取北京各个城区的天气数据并生成穿衣建议...")
for district_name, info in BEIJING_DISTRICTS.items():
    print(f"\n获取 {district_name} 的天气预报 (人物: {info['character']})...")
    district_forecast = scrape_weather_forecast(district_name, info['code'])
    if district_forecast:
        # print(f"成功获取 {district_name} 的天气数据！") # 可以取消注释进行调试
        
        # 为每个预报添加穿衣建议
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
        # 打印部分数据以验证
        print(f"  {district_name} 的穿衣建议:")
        for item in district_forecast:
            print(f"    日期: {item['date']}, 天气: {item['weather']}, 温度: {item['temperature']}, 降水: {item['precipitation']}, 穿衣建议: {item['clothing_advice']}")
    else:
        print(f"未能获取 {district_name} 的天气数据。")

if all_districts_weather:
    print("\n所有北京城区的未来5天天气预报及穿衣建议获取完成。数据已存储在 `all_districts_weather` 变量中。")
    # 打印最终结果（可选，如果数据量大，可能会很长）
    # import json
    # print(json.dumps(all_districts_weather, ensure_ascii=False, indent=2))
else:
    print("未能获取任何北京城区的天气数据，请检查网络连接、网站结构或代码。")
