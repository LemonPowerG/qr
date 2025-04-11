from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import qrcode
import os
from datetime import datetime
import pymysql
from functools import wraps
import hashlib
from urllib.parse import urlparse

# Use PyMySQL instead of mysqlclient
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes session lifetime

# MySQL connection configuration
def get_db_connection():
    if 'DATABASE_URL' in os.environ:
        url = urlparse(os.environ['DATABASE_URL'])
        return pymysql.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='feedback_system',
            cursorclass=pymysql.cursors.DictCursor
        )

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('გთხოვთ გაიაროთ ავტორიზაცია', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('გთხოვთ გაიაროთ ავტორიზაცია', 'error')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback/<int:branch_id>', methods=['GET', 'POST'])
def feedback(branch_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get branch information
            cursor.execute('SELECT * FROM branch WHERE id = %s', (branch_id,))
            branch = cursor.fetchone()
            
            if not branch:
                flash('ფილიალი ვერ მოიძებნა', 'error')
                return redirect(url_for('index'))
            
            if request.method == 'POST':
                # Get all ratings
                service_rating = request.form.get('service_rating')
                cleanliness_rating = request.form.get('cleanliness_rating')
                staff_rating = request.form.get('staff_rating')
                waiting_time_rating = request.form.get('waiting_time_rating')
                overall_rating = request.form.get('overall_rating')
                comment = request.form.get('comment')
                
                # Validate ratings
                if not all([service_rating, cleanliness_rating, staff_rating, 
                          waiting_time_rating, overall_rating]):
                    flash('გთხოვთ შეავსოთ ყველა შეფასება', 'error')
                    return render_template('feedback.html', branch=branch)
                
                # Insert feedback
                cursor.execute('''
                    INSERT INTO feedback (
                        branch_id, service_rating, cleanliness_rating, 
                        staff_rating, waiting_time_rating, overall_rating, 
                        comment, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    branch_id, service_rating, cleanliness_rating,
                    staff_rating, waiting_time_rating, overall_rating,
                    comment, datetime.utcnow()
                ))
                conn.commit()
                
                flash('მადლობა თქვენი უკუკავშირისთვის!', 'success')
                return redirect(url_for('thank_you'))
            
            return render_template('feedback.html', branch=branch)
    finally:
        conn.close()

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/admin')
@admin_required
def admin():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    per_page = 10  # Number of branches per page
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get total count for pagination
            if search_query:
                cursor.execute('SELECT COUNT(*) as total FROM branch WHERE name LIKE %s OR location LIKE %s',
                             (f'%{search_query}%', f'%{search_query}%'))
            else:
                cursor.execute('SELECT COUNT(*) as total FROM branch')
            total = cursor.fetchone()['total']
            
            # Calculate pagination
            total_pages = (total + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # Get branches with pagination and search
            if search_query:
                cursor.execute('''
                    SELECT * FROM branch 
                    WHERE name LIKE %s OR location LIKE %s 
                    ORDER BY name 
                    LIMIT %s OFFSET %s
                ''', (f'%{search_query}%', f'%{search_query}%', per_page, offset))
            else:
                cursor.execute('SELECT * FROM branch ORDER BY name LIMIT %s OFFSET %s',
                             (per_page, offset))
            branches = cursor.fetchall()
            
            return render_template('admin/dashboard.html',
                                branches=branches,
                                page=page,
                                total_pages=total_pages,
                                search_query=search_query)
    finally:
        conn.close()

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt - Username: {username}")  # Debug info
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
                user = cursor.fetchone()
                
                print(f"User found in database: {user is not None}")  # Debug info
                
                if user:
                    print(f"User data - ID: {user['id']}, Is Admin: {user['is_admin']}")  # Debug info
                    # Use MD5 hash for password verification
                    password_hash = hashlib.md5(password.encode()).hexdigest()
                    password_valid = (password_hash == user['password_hash'])
                    print(f"Password valid: {password_valid}")  # Debug info
                    print(f"Input hash: {password_hash}")  # Debug info
                    print(f"Stored hash: {user['password_hash']}")  # Debug info
                    
                    if password_valid:
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        session['is_admin'] = user['is_admin']
                        session.permanent = True
                        print("Login successful, redirecting to admin")  # Debug info
                        return redirect(url_for('admin'))
                    else:
                        print("Invalid password")  # Debug info
                else:
                    print("User not found")  # Debug info
                
                flash('არასწორი მომხმარებელი ან პაროლი', 'error')
        finally:
            conn.close()
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/branch/add', methods=['GET', 'POST'])
@admin_required
def add_branch():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Insert branch
                cursor.execute(
                    'INSERT INTO branch (name, location) VALUES (%s, %s)',
                    (name, location)
                )
                branch_id = cursor.lastrowid
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                feedback_url = url_for('feedback', branch_id=branch_id, _external=True)
                print(f"Generating QR code for URL: {feedback_url}")  # Debug info
                
                qr.add_data(feedback_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                qr_path = f"qr_codes/{branch_id}.png"
                full_path = os.path.join('static', qr_path)
                
                print(f"Saving QR code to: {full_path}")  # Debug info
                print(f"Directory exists: {os.path.exists(os.path.dirname(full_path))}")  # Debug info
                print(f"Directory is writable: {os.access(os.path.dirname(full_path), os.W_OK)}")  # Debug info
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Save the image
                try:
                    img.save(full_path)
                    print(f"QR code saved successfully to {full_path}")  # Debug info
                    print(f"File exists after save: {os.path.exists(full_path)}")  # Debug info
                    print(f"File size: {os.path.getsize(full_path)} bytes")  # Debug info
                except Exception as e:
                    print(f"Error saving QR code: {str(e)}")  # Debug info
                    print(f"Current working directory: {os.getcwd()}")  # Debug info
                    flash('QR კოდის შენახვა ვერ მოხერხდა', 'error')
                    return redirect(url_for('admin'))
                
                # Update branch with QR code path
                cursor.execute(
                    'UPDATE branch SET qr_code_path = %s WHERE id = %s',
                    (qr_path, branch_id)
                )
                conn.commit()
                
                flash('ფილიალი წარმატებით დაემატა', 'success')
                return redirect(url_for('admin'))
        finally:
            conn.close()
    
    return render_template('admin/add_branch.html')

@app.route('/admin/branch/delete/<int:branch_id>', methods=['POST'])
@admin_required
def delete_branch(branch_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get QR code path before deleting
            cursor.execute('SELECT qr_code_path FROM branch WHERE id = %s', (branch_id,))
            branch = cursor.fetchone()
            
            if branch and branch['qr_code_path']:
                # Delete QR code file
                qr_path = os.path.join('static', branch['qr_code_path'])
                if os.path.exists(qr_path):
                    os.remove(qr_path)
            
            # Delete branch and related feedback
            cursor.execute('DELETE FROM feedback WHERE branch_id = %s', (branch_id,))
            cursor.execute('DELETE FROM branch WHERE id = %s', (branch_id,))
            conn.commit()
            
            flash('ფილიალი წარმატებით წაიშალა', 'success')
    except Exception as e:
        print(f"Error deleting branch: {str(e)}")
        flash('ფილიალის წაშლა ვერ მოხერხდა', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin'))

@app.route('/admin/feedback/<int:branch_id>')
@admin_required
def view_feedback(branch_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get branch information
            cursor.execute('SELECT * FROM branch WHERE id = %s', (branch_id,))
            branch = cursor.fetchone()
            
            if not branch:
                flash('ფილიალი ვერ მოიძებნა', 'error')
                return redirect(url_for('admin'))
            
            # Get feedback statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_feedback,
                    
                    -- Average ratings
                    AVG(service_rating) as avg_service_rating,
                    AVG(cleanliness_rating) as avg_cleanliness_rating,
                    AVG(staff_rating) as avg_staff_rating,
                    AVG(waiting_time_rating) as avg_waiting_time_rating,
                    AVG(overall_rating) as avg_overall_rating,
                    
                    -- Rating categories count
                    COUNT(CASE WHEN overall_rating <= 6 THEN 1 END) as negative_count,
                    COUNT(CASE WHEN overall_rating BETWEEN 7 AND 8 THEN 1 END) as neutral_count,
                    COUNT(CASE WHEN overall_rating >= 9 THEN 1 END) as positive_count,
                    
                    -- Service rating distribution
                    COUNT(CASE WHEN service_rating <= 6 THEN 1 END) as service_negative,
                    COUNT(CASE WHEN service_rating BETWEEN 7 AND 8 THEN 1 END) as service_neutral,
                    COUNT(CASE WHEN service_rating >= 9 THEN 1 END) as service_positive,
                    
                    -- Cleanliness rating distribution
                    COUNT(CASE WHEN cleanliness_rating <= 6 THEN 1 END) as cleanliness_negative,
                    COUNT(CASE WHEN cleanliness_rating BETWEEN 7 AND 8 THEN 1 END) as cleanliness_neutral,
                    COUNT(CASE WHEN cleanliness_rating >= 9 THEN 1 END) as cleanliness_positive,
                    
                    -- Staff rating distribution
                    COUNT(CASE WHEN staff_rating <= 6 THEN 1 END) as staff_negative,
                    COUNT(CASE WHEN staff_rating BETWEEN 7 AND 8 THEN 1 END) as staff_neutral,
                    COUNT(CASE WHEN staff_rating >= 9 THEN 1 END) as staff_positive,
                    
                    -- Waiting time rating distribution
                    COUNT(CASE WHEN waiting_time_rating <= 6 THEN 1 END) as waiting_negative,
                    COUNT(CASE WHEN waiting_time_rating BETWEEN 7 AND 8 THEN 1 END) as waiting_neutral,
                    COUNT(CASE WHEN waiting_time_rating >= 9 THEN 1 END) as waiting_positive
                FROM feedback 
                WHERE branch_id = %s
            ''', (branch_id,))
            stats = cursor.fetchone()
            
            # Get feedback comments
            cursor.execute('''
                SELECT * FROM feedback 
                WHERE branch_id = %s 
                ORDER BY created_at DESC
            ''', (branch_id,))
            feedbacks = cursor.fetchall()
            
            return render_template('admin/feedback.html',
                                branch=branch,
                                feedbacks=feedbacks,
                                stats=stats)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 