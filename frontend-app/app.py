import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import requests

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
MEDIA_FOLDER = '/app/media'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            resp = requests.post(f"{BACKEND_URL}/auth/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                user = resp.json()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                # ИЗМЕНЕНО: Сохраняем статус сотрудника в сессию
                session['is_staff'] = user.get('is_staff', False) 
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials', 'error')
        except:
            flash('Backend unavailable', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # ИЗМЕНЕНО: Добавлен is_staff в параметры запроса к бэкенду
    params = {
        'user_id': session['user_id'], 
        'is_admin': session['is_admin'],
        'is_staff': session.get('is_staff', False)
    }
    resp = requests.get(f"{BACKEND_URL}/tickets/", params=params)
    tickets = resp.json() if resp.status_code == 200 else []
    
    return render_template('dashboard.html', tickets=tickets, user=session)

@app.route('/create_ticket', methods=['POST'])
def create_ticket():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'creator_id': session['user_id']
    }
    requests.post(f"{BACKEND_URL}/tickets/", json=data)
    return redirect(url_for('dashboard'))

@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    t_resp = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
    r_resp = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}/reports")
    
    if t_resp.status_code != 200: return "Not Found", 404
    
    return render_template('ticket_detail.html', ticket=t_resp.json(), reports=r_resp.json())

# НОВЫЙ МАРШРУТ: Обновление статуса/редактирование заявки
@app.route('/ticket/<int:ticket_id>/update', methods=['POST'])
def update_ticket(ticket_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # Собираем данные из формы (могут прийти или поля текста, или статус)
    data = {
        "status": request.form.get('status'),
        "title": request.form.get('title'),
        "description": request.form.get('description')
    }
    # Удаляем None значения, чтобы не затереть данные на бэкенде
    data = {k: v for k, v in data.items() if v is not None}
    
    params = {
        'user_id': session['user_id'],
        'is_admin': session['is_admin'],
        'is_staff': session.get('is_staff', False)
    }
    
    resp = requests.put(f"{BACKEND_URL}/tickets/{ticket_id}", json=data, params=params)
    
    if resp.status_code == 200:
        flash('Ticket updated', 'success')
    else:
        flash(f"Error: {resp.json().get('detail', 'Update failed')}", 'error')
        
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))

@app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket(ticket_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # ИЗМЕНЕНО: Теперь передаем только флаг админа, так как только он может удалять
    params = {'is_admin': session.get('is_admin', False)}
    resp = requests.delete(f"{BACKEND_URL}/tickets/{ticket_id}", params=params)
    
    if resp.status_code != 200:
        flash(resp.json().get('detail', 'Error'), 'error')
    else:
        flash('Ticket deleted', 'success')
        
    return redirect(url_for('dashboard'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return "Access Denied", 403
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        is_staff = request.form.get('is_staff') == 'on' # ИЗМЕНЕНО: Получаем галочку сотрудника
        
        requests.post(f"{BACKEND_URL}/auth/users", json={
            "username": username, 
            "password": password, 
            "is_admin": is_admin,
            "is_staff": is_staff # ИЗМЕНЕНО: Отправляем на бэкенд
        })
        flash(f'User {username} created', 'success')
        
    return render_template('admin.html')

@app.route('/media/<path:filename>')
def serve_media(filename):
    if 'user_id' not in session: return "Unauthorized", 401
    return send_from_directory(MEDIA_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)