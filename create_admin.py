from app import app, get_db_connection
from werkzeug.security import generate_password_hash

def create_admin():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if admin already exists
            cursor.execute('SELECT * FROM user WHERE username = %s', ('admin',))
            admin = cursor.fetchone()
            
            if admin:
                print("ადმინისტრატორი უკვე არსებობს!")
                return

            # Create admin user
            password_hash = generate_password_hash('admin123')  # შეცვალეთ პაროლი!
            cursor.execute(
                'INSERT INTO user (username, password_hash, is_admin) VALUES (%s, %s, %s)',
                ('admin', password_hash, True)
            )
            conn.commit()
            print("ადმინისტრატორი წარმატებით შეიქმნა!")
    finally:
        conn.close()

if __name__ == '__main__':
    create_admin() 