import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'root')
        self.database = os.getenv('DB_NAME', 'vamsify_llm_chat')
        self.connection = None
        self._init_db()

    def _get_connection(self):
        """Create a database connection."""
        try:
            # First connect without database to create it if needed
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                connection.close()
            
            # Now connect to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def _init_db(self):
        """Initialize database tables."""
        conn = self._get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            
            # Create conversations table with JSON history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255),
                    history JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Check if history column exists (migration for existing table)
            cursor.execute("SHOW COLUMNS FROM conversations LIKE 'history'")
            if not cursor.fetchone():
                print("Migrating conversations table: adding history column...")
                cursor.execute("ALTER TABLE conversations ADD COLUMN history JSON")
            
            # Drop messages table if exists (migration)
            cursor.execute("DROP TABLE IF EXISTS messages")
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully!")

    def execute_query(self, query, params=None):
        """Execute a query (INSERT, UPDATE, DELETE)."""
        conn = self._get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error executing query: {e}")
            finally:
                cursor.close()
                conn.close()

    def fetch_all(self, query, params=None):
        """Fetch all results (SELECT)."""
        conn = self._get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                print(f"Error fetching data: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
        return []

    def fetch_one(self, query, params=None):
        """Fetch one result (SELECT)."""
        conn = self._get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchone()
            except Error as e:
                print(f"Error fetching data: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
        return None
