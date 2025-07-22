from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "gizli_anahtar"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    success = session.pop('success', None)
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('main'))
        else:
            error = 'Hatalı kullanıcı adı veya şifre!'
    # Sadece POST sonrası error parametresi gönderilecek
    if request.method == 'POST':
        return render_template('login.html', error=error, success=success)
    if success:
        return render_template('login.html', success=success)
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('reg_username')
    password = request.form.get('reg_password')
    password2 = request.form.get('reg_password2')
    if not username or not password or not password2:
        session['success'] = 'Tüm alanları doldurun!'
        return redirect(url_for('login'))
    if password != password2:
        session['success'] = 'Şifreler eşleşmiyor!'
        return redirect(url_for('login'))
    if User.query.filter_by(username=username).first():
        session['success'] = 'Bu kullanıcı adı zaten alınmış!'
        return redirect(url_for('login'))
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    session['success'] = 'Kayıt başarılı! Şimdi giriş yapabilirsiniz.'
    return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('sitehtml.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('users.db'):
        with app.app_context():
            db.create_all()
            # Varsayılan bir kullanıcı ekle (admin/1234)
            if not User.query.filter_by(username='admin').first():
                db.session.add(User(username='admin', password='1234'))
                db.session.commit()
    app.run(debug=True) 
