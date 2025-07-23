from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail, Message
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__)
app.secret_key = "gizli_anahtar"
# Veritabanı bağlantısı: Önce ortam değişkeni, yoksa SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Mail ayarları (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
mail = Mail(app)

# Kullanıcı modeli (güncellenmiş)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    banned = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)

# Blog yazısı modeli
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# SSS modeli
class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)

# Admin giriş bilgileri
ADMIN_EMAIL = 'selamimertileri321@gmail.com'
ADMIN_PASSWORD = '123456aA.'

# E-posta doğrulama için serializer
serializer = URLSafeTimedSerializer(app.secret_key)

# Magic link için serializer
magic_serializer = URLSafeTimedSerializer(app.secret_key)

@app.route('/', methods=['GET', 'POST'])
def login():
    success = session.pop('success', None)
    error = None
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        if len(username_or_email) < 8 or len(password) < 8:
            flash('Kullanıcı adı ve şifre en az 8 karakter olmalı!', 'danger')
        elif username_or_email == 'admin':
            flash('Admin kullanıcısı ile giriş yapılamaz.', 'danger')
        else:
            user = User.query.filter(
                ((User.username == username_or_email) | (User.email == username_or_email)) &
                (User.password == password)
            ).first()
            if user:
                if user.banned:
                    flash('Bu kullanıcı banlanmıştır.', 'danger')
                else:
                    try:
                        token = magic_serializer.dumps(user.email, salt='magic-login')
                        magic_url = url_for('magic_login', token=token, _external=True)
                        msg = Message('Giriş Doğrulama Linki', recipients=[user.email])
                        msg.body = f'Giriş yapmak için bu linke tıklayın (10 dakika geçerli): {magic_url}'
                        mail.send(msg)
                        session['pending_email'] = user.email
                        flash('Giriş linki e-posta adresinize gönderildi! Lütfen e-postanızı kontrol edin.', 'success')
                    except Exception as e:
                        flash('E-posta gönderilemedi: ' + str(e), 'danger')
            else:
                flash('Hatalı kullanıcı adı/e-posta veya şifre!', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html', success=success)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('reg_username')
    email = request.form.get('reg_email')
    password = request.form.get('reg_password')
    password2 = request.form.get('reg_password2')
    if not username or not email or not password or not password2:
        flash('Tüm alanları doldurun!', 'danger')
        return redirect(url_for('login'))
    if len(username) < 8 or len(password) < 8:
        flash('Kullanıcı adı ve şifre en az 8 karakter olmalı!', 'danger')
        return redirect(url_for('login'))
    if password != password2:
        flash('Şifreler eşleşmiyor!', 'danger')
        return redirect(url_for('login'))
    if User.query.filter_by(username=username).first():
        flash('Bu kullanıcı adı zaten alınmış!', 'danger')
        return redirect(url_for('login'))
    if User.query.filter_by(email=email).first():
        flash('Bu e-posta adresi zaten kayıtlı!', 'danger')
        return redirect(url_for('login'))
    try:
        new_user = User(username=username, email=email, password=password, email_verified=False)
        db.session.add(new_user)
        db.session.commit()
        token = serializer.dumps(email, salt='email-verify')
        verify_url = url_for('verify_email', token=token, _external=True)
        msg = Message('E-posta Doğrulama', recipients=[email])
        msg.body = f'E-posta adresinizi doğrulamak için şu linke tıklayın: {verify_url}'
        mail.send(msg)
        flash('Kayıt başarılı! Lütfen e-posta adresinizi doğrulayın.', 'success')
    except Exception as e:
        flash('Kayıt veya e-posta gönderimi sırasında hata oluştu: ' + str(e), 'danger')
    return redirect(url_for('login'))

@app.route('/verify-email/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)
    except SignatureExpired:
        return 'Doğrulama linkinin süresi dolmuş!', 400
    except BadSignature:
        return 'Geçersiz doğrulama linki!', 400
    user = User.query.filter_by(email=email).first()
    if user:
        user.email_verified = True
        db.session.commit()
        return 'E-posta adresiniz doğrulandı! Artık giriş yapabilirsiniz.'
    return 'Kullanıcı bulunamadı!', 404

@app.route('/magic-login/<token>')
def magic_login(token):
    try:
        email = magic_serializer.loads(token, salt='magic-login', max_age=600)  # 10 dakika
    except SignatureExpired:
        return 'Doğrulama linkinin süresi dolmuş!', 400
    except BadSignature:
        return 'Geçersiz doğrulama linki!', 400
    user = User.query.filter_by(email=email).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('main'))
    return 'Kullanıcı bulunamadı!', 404

@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('sitehtml.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('reset_email')
    if not email:
        flash('E-posta adresi gerekli!', 'danger')
        return redirect(url_for('login'))
    # Burada gerçek bir kullanıcı kontrolü yapılabilir
    try:
        msg = Message('Şifre Sıfırlama', recipients=[email])
        msg.body = 'Şifre sıfırlama isteğiniz alındı. (Buraya gerçek bir link ekleyebilirsiniz.)'
        mail.send(msg)
        flash('Şifre sıfırlama e-postası gönderildi!', 'success')
    except Exception as e:
        flash('E-posta gönderilemedi: ' + str(e), 'danger')
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = 'Geçersiz admin kullanıcı adı veya şifre!'
    return render_template('admin_login.html', error=error)

@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_panel.html')

# Kullanıcıları listele
@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin_users.html', users=users)

# Kullanıcıyı banla
@app.route('/admin/users/ban/<int:user_id>', methods=['POST'])
def admin_user_ban(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    user = User.query.get_or_404(user_id)
    user.banned = True
    db.session.commit()
    flash('Kullanıcı banlandı!', 'success')
    return redirect(url_for('admin_users'))

# Kullanıcı banını kaldır
@app.route('/admin/users/unban/<int:user_id>', methods=['POST'])
def admin_user_unban(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    user = User.query.get_or_404(user_id)
    user.banned = False
    db.session.commit()
    flash('Kullanıcı banı kaldırıldı!', 'success')
    return redirect(url_for('admin_users'))

# Blog yazılarını listele
@app.route('/admin/blog')
def admin_blog():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin_blog.html', posts=posts)

# Blog yazısı ekle
@app.route('/admin/blog/add', methods=['GET', 'POST'])
def admin_blog_add():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if not title or not content:
            flash('Başlık ve içerik zorunludur!', 'danger')
        else:
            post = BlogPost(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            flash('Blog yazısı eklendi!', 'success')
            return redirect(url_for('admin_blog'))
    return render_template('admin_blog_add.html')

# Blog yazısı sil
@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
def admin_blog_delete(post_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog yazısı silindi!', 'success')
    return redirect(url_for('admin_blog'))

# SSS'leri listele
@app.route('/admin/faq')
def admin_faq():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    faqs = FAQ.query.order_by(FAQ.id.desc()).all()
    return render_template('admin_faq.html', faqs=faqs)

# SSS ekle
@app.route('/admin/faq/add', methods=['GET', 'POST'])
def admin_faq_add():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        if not question or not answer:
            flash('Soru ve cevap zorunludur!', 'danger')
        else:
            faq = FAQ(question=question, answer=answer)
            db.session.add(faq)
            db.session.commit()
            flash('SSS eklendi!', 'success')
            return redirect(url_for('admin_faq'))
    return render_template('admin_faq_add.html')

# SSS sil
@app.route('/admin/faq/delete/<int:faq_id>', methods=['POST'])
def admin_faq_delete(faq_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash('SSS silindi!', 'success')
    return redirect(url_for('admin_faq'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', email='admin@example.com', password='12345678'))
            db.session.commit()
    app.run(debug=True) 
