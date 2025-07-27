from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Ziyaretçi logları için dosya
VISITOR_LOG_FILE = 'visitor_logs.json'

def get_location_from_ip(ip_address):
    """IP adresinden konum bilgisi al"""
    # Localhost ve private IP'ler için
    if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return {
            'country': 'Local',
            'city': 'Local',
            'region': 'Local',
            'district': 'Local',
            'timezone': 'Local',
            'isp': 'Local'
        }
    
    # Requests kütüphanesi yüklü mü kontrol et
    try:
        import requests
    except ImportError:
        print("Requests kütüphanesi yüklü değil!")
        return {
            'country': 'Unknown',
            'city': 'Unknown',
            'region': 'Unknown',
            'district': 'Unknown',
            'timezone': 'Unknown',
            'isp': 'Unknown'
        }
    
    try:
        # Ücretsiz IP geolocation API'si - daha detaylı bilgi için
        response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                # İlçe bilgisini al (district)
                district = data.get('district', '')
                city = data.get('city', 'Unknown')
                region = data.get('regionName', 'Unknown')
                
                # Eğer ilçe varsa, şehir + ilçe formatında göster
                if district and district != city:
                    detailed_location = f"{city}, {district}"
                else:
                    detailed_location = city
                
                # Koordinatları kontrol et
                lat = data.get('lat')
                lon = data.get('lon')
                
                return {
                    'country': data.get('country', 'Unknown'),
                    'city': city,
                    'region': region,
                    'district': district,
                    'detailed_location': detailed_location,
                    'timezone': data.get('timezone', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'latitude': lat if lat and lat != 0 else None,
                    'longitude': lon if lon and lon != 0 else None,
                    'zip_code': data.get('zip', 'Unknown'),
                    'mobile': data.get('mobile', False),
                    'proxy': data.get('proxy', False),
                    'hosting': data.get('hosting', False)
                }
    except Exception as e:
        print(f"IP geolocation error: {e}")
    
    return {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'district': 'Unknown',
        'detailed_location': 'Unknown',
        'timezone': 'Unknown',
        'isp': 'Unknown',
        'latitude': 'Unknown',
        'longitude': 'Unknown',
        'zip_code': 'Unknown',
        'mobile': False,
        'proxy': False,
        'hosting': False
    }

def log_visitor(ip_address, user_agent, referrer=None):
    """Ziyaretçi bilgilerini logla"""
    # Konum bilgisini al
    location = get_location_from_ip(ip_address)
    
    visitor_data = {
        'ip_address': ip_address,
        'user_agent': user_agent,
        'referrer': referrer,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'country': location['country'],
        'city': location['city'],
        'region': location['region'],
        'district': location['district'],
        'detailed_location': location['detailed_location'],
        'timezone': location['timezone'],
        'isp': location['isp'],
        'latitude': location['latitude'],
        'longitude': location['longitude'],
        'zip_code': location['zip_code'],
        'mobile': location['mobile'],
        'proxy': location['proxy'],
        'hosting': location['hosting']
    }
    
    # Mevcut logları oku
    try:
        with open(VISITOR_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    
    # Yeni ziyaretçiyi ekle
    logs.append(visitor_data)
    
    # Son 1000 ziyaretçiyi tut (dosya büyümesini önle)
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    # Logları kaydet
    with open(VISITOR_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

@app.route('/')
def main():
    # Ziyaretçi bilgilerini al
    ip_address = request.remote_addr
    
    # Proxy arkasındaysa gerçek IP'yi al
    if request.headers.get('X-Forwarded-For'):
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip_address = request.headers.get('X-Real-IP')
    
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referrer = request.headers.get('Referer', 'Direct')
    
    # Ziyaretçiyi logla
    log_visitor(ip_address, user_agent, referrer)
    
    return render_template('sitehtml.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Email ayarları
        sender_email = "selamimertileri321@gmail.com"  # Gönderen email
        receiver_email = "selamimertileri321@gmail.com"  # Alıcı email (senin emailin)
        
        # Email içeriği
        subject = f"Portfolio Sitesinden Yeni Mesaj - {name}"
        body = f"""
        Yeni bir mesaj aldınız!
        
        Gönderen: {name}
        Email: {email}
        
        Mesaj:
        {message}
        """
        
        # Email oluştur
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # SMTP ayarları (Gmail için)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Gmail uygulama şifresi kullan (normal şifre değil!)
        password = "keex cyux bsth xvax"  # Gmail uygulama şifresi
        
        # Email gönder
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        flash('Mesajınız başarıyla gönderildi!', 'success')
        return redirect(url_for('main'))
        
    except Exception as e:
        flash('Mesaj gönderilirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('main'))

@app.route('/admin/logs')
def view_logs():
    """Ziyaretçi loglarını görüntüle"""
    try:
        with open(VISITOR_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    except Exception as e:
        print(f"Logs error: {e}")
        logs = []
    
    # Logları ters sırala (en yeni üstte)
    logs.reverse()
    
    return render_template('admin_logs.html', logs=logs)

@app.route('/admin/stats')
def view_stats():
    """Ziyaretçi istatistiklerini görüntüle"""
    try:
        with open(VISITOR_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    except Exception as e:
        print(f"Stats error: {e}")
        logs = []
    
    # İstatistikler
    total_visitors = len(logs)
    unique_ips = len(set(log['ip_address'] for log in logs))
    
    # Son 24 saat
    from datetime import datetime, timedelta
    now = datetime.now()
    last_24h = [log for log in logs if datetime.fromisoformat(log['timestamp']) > now - timedelta(hours=24)]
    
    # En çok ziyaret eden IP'ler
    ip_counts = {}
    for log in logs:
        ip = log['ip_address']
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # En çok ziyaret eden ülkeler
    country_counts = {}
    for log in logs:
        country = log.get('country', 'Unknown')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # En çok ziyaret eden şehirler
    city_counts = {}
    for log in logs:
        city = log.get('city', 'Unknown')
        country = log.get('country', 'Unknown')
        if city != 'Unknown':
            city_key = f"{city}, {country}"
            city_counts[city_key] = city_counts.get(city_key, 0) + 1
    
    top_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    stats = {
        'total_visitors': total_visitors,
        'unique_visitors': unique_ips,
        'last_24h': len(last_24h),
        'top_ips': top_ips,
        'top_countries': top_countries,
        'top_cities': top_cities
    }
    
    return render_template('admin_stats.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True) 
