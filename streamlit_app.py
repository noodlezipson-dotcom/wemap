import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="Open-Meteo Interactive Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.markdown("""
<div style="text-align: center;">
    <h1>🌤️ Open-Meteo Interactive Weather Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# 说明文字
st.markdown("""
<div style="background-color: #f0f2f6; padding: 1rem; border-radius: 10px; border-left: 5px solid #1f77b4; margin-bottom: 1rem;">
    <strong>지도에서 위치를 클릭하면 해당 지역의 시간별 기온 데이터를 불러옵니다.</strong>
</div>
""", unsafe_allow_html=True)

# API函数 - 直接定义在主文件中
@st.cache_data(ttl=3600)  # 缓存1小时
def get_current_weather(latitude, longitude):
    """获取当前天气数据"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current_weather': 'true',
        'timezone': 'auto'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"天气API请求失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"获取天气数据时出错: {e}")
        return None

@st.cache_data(ttl=3600)  # 缓存1小时
def get_detailed_forecast(latitude, longitude):
    """获取详细天气预报"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability',
        'daily': 'temperature_2m_max,temperature_2m_min,sunrise,sunset',
        'timezone': 'auto',
        'forecast_days': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"获取详细天气预报时出错: {e}")
        return None

def get_weather_description(weather_code):
    """将天气代码转换为描述性文字"""
    weather_codes = {
        0: "맑음",
        1: "대체로 맑음",
        2: "부분적으로 흐림",
        3: "흐림",
        45: "안개",
        48: "서리 안개",
        51: "이슬비: 약함",
        53: "이슬비: 중간",
        55: "이슬비: 강함",
        61: "비: 약함",
        63: "비: 중간",
        65: "비: 강함",
        80: "소나기: 약함",
        81: "소나기: 중간",
        82: "소나기: 강함",
        95: "뇌우",
        96: "우박을 동반한 뇌우",
        99: "강한 우박을 동반한 뇌우"
    }
    return weather_codes.get(weather_code, "알 수 없음")

def main():
    # 主要功能区域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 지역 선택 (지도를 클릭하세요)")
        
        # 地图说明
        st.info("**지도를 클릭하면 해당 지역의 날씨 데이터를 가져옵니다.**")
        
        # 使用默认地图位置
        default_location = [37.5665, 126.9780]  # 首尔
        
        # 创建地图
        map_data = pd.DataFrame({
            'lat': [default_location[0]],
            'lon': [default_location[1]]
        })
        
        st.map(map_data, zoom=10)
        
        # 手动输入坐标的选项
        with st.expander("또는 좌표를 직접 입력하세요"):
            coord_col1, coord_col2 = st.columns(2)
            with coord_col1:
                latitude = st.number_input("위도", value=37.5665, format="%.4f", key="lat_input")
            with coord_col2:
                longitude = st.number_input("경도", value=126.9780, format="%.4f", key="lon_input")
            
            use_custom_coords = st.button("이 좌표로 날씨 확인하기", key="custom_coords_btn")
    
    with col2:
        st.subheader("2. 날씨 정보")
        
        # 确定使用哪个坐标
        lat, lon = default_location
        use_api = False
        
        # 检查是否有自定义坐标被使用
        if use_custom_coords:
            lat, lon = latitude, longitude
            use_api = True
        
        # 显示天气信息的按钮
        if use_api or st.button("현재 위치의 날씨 보기", type="primary", key="current_weather_btn"):
            display_weather_data(lat, lon)
        else:
            st.info("📍 지도에서 위치를 클릭하거나 좌표를 입력하여 날씨 정보를 확인하세요.")
    
    # 页脚
    st.markdown("---")
    st.markdown("© 2024 Weather Dashboard | Powered by Open-Meteo API")

def display_weather_data(latitude, longitude):
    """显示天气数据"""
    # 获取当前天气
    with st.spinner("날씨 데이터를 불러오는 중..."):
        current_weather = get_current_weather(latitude, longitude)
        detailed_forecast = get_detailed_forecast(latitude, longitude)
    
    if not current_weather:
        st.error("날씨 데이터를 불러오는데 실패했습니다. 다시 시도해주세요.")
        return
    
    # 位置信息
    st.success(f"📍 선택한 위치: 위도 {latitude:.4f}, 경도 {longitude:.4f}")
    
    # 当前天气卡片
    display_current_weather(current_weather)
    
    # 详细预报
    if detailed_forecast:
        display_detailed_forecast(detailed_forecast)

def display_current_weather(weather_data):
    """显示当前天气信息"""
    current = weather_data.get('current_weather', {})
    
    # 创建天气卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp = current.get('temperature', 'N/A')
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
            <h3>🌡️ 온도</h3>
            <h2>{temp}°C</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        windspeed = current.get('windspeed', 'N/A')
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
            <h3>💨 풍속</h3>
            <h2>{windspeed} km/h</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        winddir = current.get('winddirection', 'N/A')
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
            <h3>🧭 풍향</h3>
            <h2>{winddir}°</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        weather_code = current.get('weathercode', 0)
        weather_desc = get_weather_description(weather_code)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
            <h3>☀️ 날씨</h3>
            <h4>{weather_desc}</h4>
        </div>
        """, unsafe_allow_html=True)

def display_detailed_forecast(forecast_data):
    """显示详细天气预报"""
    st.subheader("3. 시간별 기상 예보")
    
    # 显示温度图表
    hourly = forecast_data.get('hourly', {})
    if hourly and 'time' in hourly and 'temperature_2m' in hourly:
        # 创建温度数据表格
        times = hourly['time'][:24]  # 接下来24小时
        temperatures = hourly['temperature_2m'][:24]
        
        # 创建数据框
        df = pd.DataFrame({
            '시간': [t[11:16] for t in times],  # 提取时间部分
            '온도 (°C)': temperatures
        })
        
        # 显示表格
        st.dataframe(df, use_container_width=True)
        
        # 显示简单图表
        st.line_chart(df.set_index('시간'))

if __name__ == "__main__":
    main()
