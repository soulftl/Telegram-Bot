import requests
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
import numpy as np
from scipy.interpolate import make_interp_spline
from matplotlib.dates import HourLocator, DateFormatter
import math
matplotlib.use('Agg')

def get_openmeteo_weather():
    """Get weather data from OpenMeteo API for Yaroslavl."""
    try:
        # Координаты Ярославля
        latitude = 57.6261
        longitude = 39.8845
        
        # Получаем текущую погоду, прогноз и почасовую температуру
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,apparent_temperature,relative_humidity_2m,weathercode,wind_speed_10m,pressure_msl&hourly=temperature_2m&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Europe%2FMoscow&forecast_days=2"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Добавляем логирование для отладки
        logging.info(f"OpenMeteo API response: {data}")
        
        if not data or 'current' not in data or 'daily' not in data or 'hourly' not in data:
            logging.error("Invalid response from weather API")
            return None
            
        return {
            'current': data['current'],
            'daily': data['daily'],
            'hourly': data['hourly']
        }
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in get_openmeteo_weather: {e}")
        return None

def get_weather_description(weathercode):
    """Get weather description from weather code."""
    weather_descriptions = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Облачно с прояснениями",
        45: "Туман",
        48: "Изморозь",
        51: "Легкая морось",
        53: "Умеренная морось",
        55: "Сильная морось",
        61: "Небольшой дождь",
        63: "Умеренный дождь",
        65: "Сильный дождь",
        71: "Небольшой снег",
        73: "Умеренный снег",
        75: "Сильный снег",
        77: "Снежные зерна",
        80: "Небольшой ливень",
        81: "Умеренный ливень",
        82: "Сильный ливень",
        85: "Небольшой снегопад",
        86: "Сильный снегопад",
        95: "Гроза",
        96: "Гроза с небольшим градом",
        99: "Гроза с сильным градом"
    }
    return weather_descriptions.get(weathercode, "Неизвестно")

def get_weather_emoji(weathercode):
    emoji_map = {
        0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️", 45: "🌫", 48: "🌫",
        51: "🌦", 53: "🌦", 55: "🌧", 56: "🌧", 57: "🌧",
        61: "🌦", 63: "🌧", 65: "🌧", 66: "🌧", 67: "🌧",
        71: "🌨", 73: "❄️", 75: "❄️", 77: "❄️",
        80: "🌦", 81: "🌧", 82: "🌧",
        85: "🌨", 86: "❄️",
        95: "⛈", 96: "⛈", 99: "⛈"
    }
    return emoji_map.get(weathercode, "🌤")

def generate_temperature_graph(weather_data):
    """Generate a beautiful and clear temperature graph for today's hourly forecast."""
    try:
        if not weather_data or 'hourly' not in weather_data:
            return None
        hourly = weather_data['hourly']
        times = hourly['time']
        temps = hourly['temperature_2m']
        today_str = datetime.now().strftime('%Y-%m-%d')
        today_hours = [(t, temp) for t, temp in zip(times, temps) if t.startswith(today_str)]
        
        # Для графика нужно хотя бы 2 точки
        if len(today_hours) < 2:
            return None

        x = [datetime.strptime(t, '%Y-%m-%dT%H:%M') for t, _ in today_hours]
        y = [temp for _, temp in today_hours]

        plt.figure(figsize=(10, 4))

        # Интерполяция для плавной линии (делаем только если точек >= 4)
        if len(x) >= 4:
            try:
                x_num = np.array([dt.timestamp() for dt in x])
                y_num = np.array(y)
                spl = make_interp_spline(x_num, y_num, k=3)
                xnew = np.linspace(x_num.min(), x_num.max(), 200)
                y_smooth = spl(xnew)
                x_smooth = [datetime.fromtimestamp(ts) for ts in xnew]
                plt.plot(x_smooth, y_smooth, color='#FF3B3B', linewidth=2.5, zorder=1)
                plt.fill_between(x_smooth, y_smooth, alpha=0.15, color='#FF3B3B')
            except ValueError as e:
                 logging.warning(f"Could not perform spline interpolation, falling back to linear: {e}")
                 # При ошибке интерполяции используем исходные точки
                 plt.plot(x, y, color='#FF3B3B', linewidth=2.5, zorder=1)
                 plt.fill_between(x, y, alpha=0.15, color='#FF3B3B')
            except Exception as e:
                 logging.error(f"Unexpected error during spline interpolation: {e}")
                 # При любой другой ошибке интерполяции используем исходные точки
                 plt.plot(x, y, color='#FF3B3B', linewidth=2.5, zorder=1)
                 plt.fill_between(x, y, alpha=0.15, color='#FF3B3B')
        else:
            # Если точек < 4, строим график без интерполяции
            plt.plot(x, y, color='#FF3B3B', linewidth=2.5, zorder=1)
            plt.fill_between(x, y, alpha=0.15, color='#FF3B3B')

        # Рисуем точки только если их не очень много
        if len(x) <= 24:
            plt.scatter(x, y, color='#FF3B3B', s=50, zorder=2, edgecolors='white', linewidths=1.5)

        # Подписи температуры над точками (только если точек не очень много)
        if len(x) <= 24:
            for xi, yi in zip(x, y):
                try:
                    # Увеличим отступ подписи от точки
                    plt.text(xi, float(yi) + (max(y)*0.02 + 0.5), f'{round(yi)}°', ha='center', va='bottom', fontsize=9, color='#333', fontweight='bold')
                except TypeError as e:
                    logging.error(f"Error placing text label at {xi}: {e}, value: {yi}")
                    continue
                except Exception as e:
                     logging.error(f"Unexpected error placing text label at {xi}: {e}")
                     continue

        # Оформление осей и заголовка
        plt.title('График температуры на сегодня:', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Время', fontsize=11)
        plt.ylabel('Температура (°C)', fontsize=11)

        # Установка лимитов оси Y с отступом
        y_min_val = min(y) if y else 0
        y_max_val = max(y) if y else 25 # Default max if no data
        # Добавим отступ сверху, учитывая максимальное значение для подписей
        padding_top = (y_max_val - y_min_val) * 0.15 + 3 # Отступ 15% от диапазона + константа
        plt.ylim(y_min_val - 2, y_max_val + padding_top) 

        # Оформление оси X: подписи каждые 3 часа
        plt.gca().xaxis.set_major_locator(HourLocator(interval=3))
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))

        plt.grid(True, linestyle='--', alpha=0.3, linewidth=1)
        plt.tight_layout()
        plt.gcf().autofmt_xdate()

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        img_str = base64.b64encode(buf.getvalue()).decode()
        return img_str
    except Exception as e:
        logging.error(f"Error generating temperature graph: {e}")
        return None

def smart_round(temp):
    """Round temperature according to custom rules: X.5 rounds down to X, X.6+ rounds up to X+1."""
    return math.ceil(temp - 0.5) # Реализация округления

def format_weather_message(weather_data):
    """
    Форматирует данные о погоде в читаемое сообщение
    Включает текущую температуру, описание погоды и прогноз
    """
    try:
        if not weather_data:
            return "Извините, не удалось получить данные о погоде."

        current = weather_data['current']
        daily = weather_data['daily']
        
        # Эмодзи по погоде
        current_weather_emoji = get_weather_emoji(current['weathercode'])
        tomorrow_weather_emoji = get_weather_emoji(daily['weathercode'][1])

        # Описание текущей погоды
        current_weather_description = get_weather_description(current['weathercode'])
        
        # Форматируем текущую погоду
        message = (
            f"{current_weather_emoji} Текущая погода:\n"
            f"🌡 Температура: {smart_round(current['temperature_2m'])}°C\n"
            f"🌡 Ощущается как: {smart_round(current['apparent_temperature'])}°C\n"
            f"{current_weather_emoji} {current_weather_description}\n\n"
        )
        
        # Прогноз на завтра
        tomorrow_max_temp = smart_round(daily['temperature_2m_max'][1])
        tomorrow_weather_description = get_weather_description(daily['weathercode'][1])
        
        message += (
            f"📅 Прогноз на завтра:\n"
            f"🌡 Температура: {tomorrow_max_temp}°C\n"
            f"{tomorrow_weather_emoji} {tomorrow_weather_description}"
        )
        
        return message
        
    except Exception as e:
        logging.error(f"Ошибка при форматировании сообщения о погоде: {e}", exc_info=True)
        return "Извините, произошла ошибка при форматировании прогноза погоды."

def generate_hourly_temperature_graph_image(hourly_data):
    """Generate a matplotlib graph image of hourly temperatures for today."""
    try:
        if not hourly_data or 'time' not in hourly_data or 'temperature_2m' not in hourly_data:
            logging.warning("Missing hourly data for graph generation.")
            return None

        times = [datetime.fromisoformat(ts) for ts in hourly_data['time']]
        temperatures = hourly_data['temperature_2m']

        # Filter data for today
        today_date = datetime.now().date()
        filtered_times = []
        filtered_temps = []
        for i, t in enumerate(times):
            if t.date() == today_date:
                filtered_times.append(t)
                filtered_temps.append(temperatures[i])
        
        if not filtered_times:
            logging.warning("No hourly data available for today for graph generation.")
            return None

        plt.style.use('ggplot') # Use a clean ggplot style
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

        ax.plot(filtered_times, filtered_temps, marker='o', linestyle='-', color='#FF6347', linewidth=2)
        ax.fill_between(filtered_times, min(filtered_temps) - 2, filtered_temps, color='#FF6347', alpha=0.1) # Shaded area

        # Add temperature labels on top of each point
        for i, temp in enumerate(filtered_temps):
            ax.text(filtered_times[i], temp + 0.5, f'{int(temp)}°', ha='center', va='bottom', fontsize=9, color='#333')

        # Customize the plot
        ax.set_title('График температуры на сегодня:', fontsize=16, pad=20)
        ax.set_xlabel('Время', fontsize=12)
        ax.set_ylabel('Температура (°C)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(HourLocator(interval=3)) # Show ticks every 3 hours
        fig.autofmt_xdate() # Rotate x-axis labels for better readability
        
        # Adjust y-axis limits to provide some padding
        min_temp = min(filtered_temps)
        max_temp = max(filtered_temps)
        ax.set_ylim(min_temp - 2, max_temp + 3) # Add padding

        # Save the plot to a BytesIO object and encode it to base64
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close(fig) # Close the figure to free up memory
        
        return buf.getvalue()

    except Exception as e:
        logging.error(f"Error generating hourly temperature graph image: {e}", exc_info=True)
        return None 