from app import get_db_connection
from werkzeug.security import generate_password_hash

def check_database():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Drop existing tables if they exist
            cursor.execute('DROP TABLE IF EXISTS feedback')
            cursor.execute('DROP TABLE IF EXISTS branch')
            cursor.execute('DROP TABLE IF EXISTS user')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE user (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(120) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create branches table
            cursor.execute('''
                CREATE TABLE branch (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(200) NOT NULL,
                    qr_code_path VARCHAR(200)
                )
            ''')
            
            # Create feedback table
            cursor.execute('''
                CREATE TABLE feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    branch_id INT NOT NULL,
                    rating INT NOT NULL,
                    comment TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (branch_id) REFERENCES branch(id)
                )
            ''')
            
            # Create admin user
            password_hash = generate_password_hash('admin123')
            cursor.execute(
                'INSERT INTO user (username, password_hash, is_admin) VALUES (%s, %s, %s)',
                ('admin', password_hash, True)
            )
            
            conn.commit()
            print("მონაცემთა ბაზა წარმატებით შეიქმნა!")
            print("ადმინისტრატორის მონაცემები:")
            print("მომხმარებელი: admin")
            print("პაროლი: admin123")
            
            # Verify admin user
            cursor.execute('SELECT * FROM user WHERE username = %s', ('admin',))
            admin = cursor.fetchone()
            if admin:
                print("\nადმინისტრატორის მონაცემები ბაზაში:")
                print(f"ID: {admin['id']}")
                print(f"Username: {admin['username']}")
                print(f"Is Admin: {admin['is_admin']}")
            else:
                print("\nშეცდომა: ადმინისტრატორი ვერ მოიძებნა ბაზაში!")
    finally:
        conn.close()

if __name__ == '__main__':
    check_database() 