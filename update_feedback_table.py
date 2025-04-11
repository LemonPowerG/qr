import pymysql
from app import get_db_connection

def update_feedback_table():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Drop existing feedback table
            cursor.execute('DROP TABLE IF EXISTS feedback')
            
            # Create new feedback table with 10-point rating scale
            cursor.execute('''
                CREATE TABLE feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    branch_id INT NOT NULL,
                    service_rating INT NOT NULL CHECK (service_rating BETWEEN 1 AND 10),
                    cleanliness_rating INT NOT NULL CHECK (cleanliness_rating BETWEEN 1 AND 10),
                    staff_rating INT NOT NULL CHECK (staff_rating BETWEEN 1 AND 10),
                    waiting_time_rating INT NOT NULL CHECK (waiting_time_rating BETWEEN 1 AND 10),
                    overall_rating INT NOT NULL CHECK (overall_rating BETWEEN 1 AND 10),
                    comment TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (branch_id) REFERENCES branch(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            print("Feedback table structure updated successfully!")
            
    except Exception as e:
        print(f"Error updating table: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_feedback_table() 