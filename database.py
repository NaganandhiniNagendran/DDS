import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class DatabaseManager:
    def __init__(self, db_path='drowsiness_system.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                full_name TEXT,
                experience_level TEXT DEFAULT 'Beginner',
                total_driving_time INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                total_alerts INTEGER DEFAULT 0,
                safety_score REAL DEFAULT 100.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT UNIQUE NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                alerts INTEGER DEFAULT 0,
                fatigue_level TEXT DEFAULT 'Normal',
                status TEXT DEFAULT 'Completed',
                metrics_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Fatigue events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fatigue_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                duration INTEGER,
                severity TEXT,
                details TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default settings
        default_settings = [
            ('eye_closed_threshold', '3', 'Seconds before triggering drowsiness alarm'),
            ('face_detection_confidence', '0.7', 'Minimum confidence for face detection'),
            ('alarm_volume', '0.8', 'Volume level for alarms (0.0-1.0)'),
            ('auto_session_timeout', '3600', 'Auto-stop session after inactivity (seconds)'),
            ('data_retention_days', '90', 'Days to keep session data')
        ]
        
        for key, value, desc in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value, description) 
                VALUES (?, ?, ?)
            ''', (key, value, desc))
        
        # Create default user if none exists
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, email, full_name, experience_level) 
                VALUES (?, ?, ?, ?)
            ''', ('default_driver', 'driver@example.com', 'Default Driver', 'Advanced'))
        
        conn.commit()
        conn.close()
    
    def get_current_user(self, username='default_driver'):
        """Get current user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, experience_level, 
                   total_driving_time, total_sessions, total_alerts, safety_score
            FROM users WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'full_name': user[3],
                'experience_level': user[4],
                'total_driving_time': user[5],
                'total_sessions': user[6],
                'total_alerts': user[7],
                'safety_score': user[8]
            }
        return None
    
    def update_user_stats(self, user_id, session_duration, alerts):
        """Update user statistics after session completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute('''
            SELECT total_driving_time, total_sessions, total_alerts 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        if stats:
            new_driving_time = stats[0] + session_duration
            new_sessions = stats[1] + 1
            new_alerts = stats[2] + alerts
            
            # Calculate new safety score
            avg_alerts_per_session = new_alerts / new_sessions if new_sessions > 0 else 0
            new_safety_score = max(0, 100 - (avg_alerts_per_session * 10))
            
            cursor.execute('''
                UPDATE users 
                SET total_driving_time = ?, total_sessions = ?, 
                    total_alerts = ?, safety_score = ?, last_active = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_driving_time, new_sessions, new_alerts, new_safety_score, user_id))
        
        conn.commit()
        conn.close()
    
    def save_session(self, user_id, session_data):
        """Save session data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions 
            (user_id, session_id, date, time, duration, alerts, fatigue_level, metrics_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, session_data['session_id'], session_data['date'],
            session_data['time'], session_data['duration'], session_data['alerts'],
            session_data['fatigue_level'], json.dumps(session_data.get('metrics', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def get_sessions(self, user_id=None, limit=None, offset=None):
        """Get sessions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT session_id, date, time, duration, alerts, fatigue_level, status
            FROM sessions
        '''
        params = []
        
        if user_id:
            query += ' WHERE user_id = ?'
            params.append(user_id)
        
        query += ' ORDER BY created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        if offset:
            query += ' OFFSET ?'
            params.append(offset)
        
        cursor.execute(query, params)
        sessions = cursor.fetchall()
        conn.close()
        
        return [{
            'session_id': session[0],
            'date': session[1],
            'time': session[2],
            'duration': session[3],
            'alerts': session[4],
            'fatigue_level': session[5],
            'status': session[6]
        } for session in sessions]
    
    def get_dashboard_stats(self, user_id=None):
        """Get dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user info
        user_query = 'SELECT * FROM users'
        if user_id:
            user_query += ' WHERE id = ?'
            cursor.execute(user_query, (user_id,))
        else:
            cursor.execute(user_query)
        
        user = cursor.fetchone()
        
        # Get session stats
        session_query = 'SELECT COUNT(*), SUM(duration), SUM(alerts) FROM sessions'
        if user_id:
            session_query += ' WHERE user_id = ?'
            cursor.execute(session_query, (user_id,))
        else:
            cursor.execute(session_query)
        
        session_stats = cursor.fetchone()
        
        # Get recent sessions for activity
        activity_query = '''
            SELECT session_id, date, time, alerts, fatigue_level 
            FROM sessions
        '''
        if user_id:
            activity_query += ' WHERE user_id = ?'
        activity_query += ' ORDER BY created_at DESC LIMIT 5'
        
        if user_id:
            cursor.execute(activity_query, (user_id,))
        else:
            cursor.execute(activity_query)
        
        recent_sessions = cursor.fetchall()
        
        conn.close()
        
        return {
            'user': {
                'id': user[0] if user else None,
                'username': user[1] if user else 'default_driver',
                'full_name': user[3] if user else 'Default Driver',
                'experience_level': user[4] if user else 'Advanced',
                'total_driving_time': user[5] if user else 0,
                'total_sessions': user[6] if user else 0,
                'total_alerts': user[7] if user else 0,
                'safety_score': user[8] if user else 100.0
            },
            'stats': {
                'total_sessions': session_stats[0] or 0,
                'total_duration': session_stats[1] or 0,
                'total_alerts': session_stats[2] or 0
            },
            'recent_activity': [{
                'session_id': session[0],
                'date': session[1],
                'time': session[2],
                'alerts': session[3],
                'fatigue_level': session[4]
            } for session in recent_sessions]
        }
    
    def get_chart_data(self, user_id=None, days=7):
        """Get data for charts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get daily data for timeline chart
        cursor.execute('''
            SELECT date, COUNT(*) as sessions, SUM(alerts) as alerts, AVG(duration) as avg_duration
            FROM sessions
            WHERE date >= date('now', '-{} days')
        '''.format(days))
        
        if user_id:
            cursor.execute('''
                SELECT date, COUNT(*) as sessions, SUM(alerts) as alerts, AVG(duration) as avg_duration
                FROM sessions
                WHERE user_id = ? AND date >= date('now', '-{} days')
                GROUP BY date
                ORDER BY date
            '''.format(days), (user_id,))
        else:
            cursor.execute('''
                SELECT date, COUNT(*) as sessions, SUM(alerts) as alerts, AVG(duration) as avg_duration
                FROM sessions
                WHERE date >= date('now', '-{} days')
                GROUP BY date
                ORDER BY date
            '''.format(days))
        
        daily_data = cursor.fetchall()
        
        # Get alert distribution
        cursor.execute('''
            SELECT fatigue_level, COUNT(*) as count
            FROM sessions
        ''')
        
        if user_id:
            cursor.execute('''
                SELECT fatigue_level, COUNT(*) as count
                FROM sessions
                WHERE user_id = ?
                GROUP BY fatigue_level
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT fatigue_level, COUNT(*) as count
                FROM sessions
                GROUP BY fatigue_level
            ''')
        
        alert_distribution = cursor.fetchall()
        
        conn.close()
        
        return {
            'timeline': [{
                'date': row[0],
                'sessions': row[1],
                'alerts': row[2],
                'avg_duration': row[3] or 0
            } for row in daily_data],
            'distribution': [{
                'level': row[0],
                'count': row[1]
            } for row in alert_distribution]
        }
    
    def get_setting(self, key, default=None):
        """Get system setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else default
    
    def update_setting(self, key, value):
        """Update system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()

# Global database instance
db = DatabaseManager()
