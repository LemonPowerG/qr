from app import get_db_connection
from werkzeug.security import generate_password_hash

def create_new_admin():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Drop existing admin
            cursor.execute('DELETE FROM user WHERE username = %s', ('admin',))
            
            # Create new admin with a simple password
            new_password = '123456'  # Simple password for testing
            password_hash = generate_password_hash(new_password)
            
            # Print the password hash for verification
            print(f"Password Hash: {password_hash}")
            
            cursor.execute(
                'INSERT INTO user (username, password_hash, is_admin) VALUES (%s, %s, %s)',
                ('admin', password_hash, True)
            )
            conn.commit()
            
            # Verify the user was created
            cursor.execute('SELECT * FROM user WHERE username = %s', ('admin',))
            admin = cursor.fetchone()
            
            if admin:
                print("\nადმინისტრატორი წარმატებით შეიქმნა!")
                print(f"მომხმარებელი: admin")
                print(f"პაროლი: {new_password}")
                print(f"ID: {admin['id']}")
                print(f"Is Admin: {admin['is_admin']}")
            else:
                print("\nშეცდომა: ადმინისტრატორი ვერ შეიქმნა!")
    finally:
        conn.close()

if __name__ == '__main__':
    create_new_admin() 