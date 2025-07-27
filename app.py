from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def main():
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

if __name__ == '__main__':
    app.run(debug=True) 
