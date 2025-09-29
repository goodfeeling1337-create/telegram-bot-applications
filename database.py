import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER UNIQUE NOT NULL,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        phone TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица заявок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        additional_info TEXT,
                        status TEXT DEFAULT 'new',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Таблица состояний пользователей (для FSM)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_states (
                        user_id INTEGER PRIMARY KEY,
                        state TEXT,
                        data TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                    )
                ''')
                
                # Таблица рассылок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS broadcasts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL,
                        sent_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("База данных инициализирована успешно")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
    
    def add_user(self, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (telegram_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (telegram_id, username, first_name, last_name))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            return False
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None
    
    def add_application(self, user_id: int, name: str, phone: str, additional_info: str = None, status: str = 'Новая') -> bool:
        """Добавление новой заявки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO applications (user_id, name, phone, additional_info, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, name, phone, additional_info, status))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления заявки: {e}")
            return False
    
    def get_applications(self, limit: int = 50) -> List[Dict]:
        """Получение списка заявок"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.*, u.telegram_id, u.username, u.first_name, u.last_name
                    FROM applications a
                    JOIN users u ON a.user_id = u.id
                    ORDER BY a.created_at DESC
                    LIMIT ?
                ''', (limit,))
                applications = cursor.fetchall()
                return [dict(app) for app in applications]
        except Exception as e:
            logger.error(f"Ошибка получения заявок: {e}")
            return []
    
    def get_application_count(self) -> int:
        """Получение количества заявок"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM applications')
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка получения количества заявок: {e}")
            return 0
    
    def get_all_users(self) -> List[Dict]:
        """Получение всех пользователей для рассылки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT id, telegram_id, username, first_name FROM users')
                users = cursor.fetchall()
                return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []
    
    def save_user_state(self, user_id: int, state: str, data: str = None):
        """Сохранение состояния пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_states (user_id, state, data, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, state, data))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния: {e}")
    
    def get_user_state(self, user_id: int) -> Optional[Dict]:
        """Получение состояния пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
                state = cursor.fetchone()
                return dict(state) if state else None
        except Exception as e:
            logger.error(f"Ошибка получения состояния: {e}")
            return None
    
    def clear_user_state(self, user_id: int):
        """Очистка состояния пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка очистки состояния: {e}")
    
    def get_incomplete_applications(self) -> List[Dict]:
        """Получение незавершенных заявок для напоминаний"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT us.*, u.telegram_id, u.username, u.first_name
                    FROM user_states us
                    JOIN users u ON us.user_id = u.telegram_id
                    WHERE us.state IN ('application_fio', 'application_phone', 'application_info')
                    AND us.updated_at < datetime('now', '-24 hours')
                ''')
                incomplete = cursor.fetchall()
                return [dict(app) for app in incomplete]
        except Exception as e:
            logger.error(f"Ошибка получения незавершенных заявок: {e}")
            return []
    
    def get_users_without_applications(self) -> List[Dict]:
        """Получение пользователей, которые не оформили заявки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.*, 
                           CASE 
                               WHEN us.state IS NOT NULL THEN us.updated_at
                               ELSE u.last_activity
                           END as last_seen
                    FROM users u
                    LEFT JOIN applications a ON u.id = a.user_id
                    LEFT JOIN user_states us ON u.telegram_id = us.user_id
                    WHERE a.id IS NULL
                    ORDER BY u.last_activity DESC
                ''')
                users = cursor.fetchall()
                return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"Ошибка получения пользователей без заявок: {e}")
            return []
    
    def delete_application(self, application_id: int) -> bool:
        """Удаление заявки по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM applications WHERE id = ?', (application_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка удаления заявки {application_id}: {e}")
            return False
    
    def update_application_status(self, application_id: int, status: str) -> bool:
        """Обновление статуса заявки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE applications SET status = ? WHERE id = ?', (status, application_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка обновления статуса заявки {application_id}: {e}")
            return False
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Получение пользователя по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else {}
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            return {}
    
    def delete_user(self, telegram_id: int) -> bool:
        """Удаление пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя {telegram_id}: {e}")
            return False
