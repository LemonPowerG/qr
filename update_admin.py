from app import get_db_connection
from werkzeug.security import generate_password_hash

def update_admin_password():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Delete existing admin
            cursor.execute('DELETE FROM user WHERE username = %s', ('admin',))
            
            # Create new admin with new password
            new_password = 'admin123'  # შეცვალეთ პაროლი!
            password_hash = generate_password_hash(new_password)
            cursor.execute(
                'INSERT INTO user (username, password_hash, is_admin) VALUES (%s, %s, %s)',
                ('admin', password_hash, True)
            )
            conn.commit()
            print("ადმინისტრატორის პაროლი წარმატებით განახლდა!")
            print(f"მომხმარებელი: admin")
            print(f"პაროლი: {new_password}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_admin_password() 