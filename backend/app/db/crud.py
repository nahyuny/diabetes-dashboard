import json
import os
from datetime import datetime
import sqlite3
import threading

# 데이터베이스 파일 경로
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "../../data/database.db"))
DB_DIR = os.path.dirname(DB_PATH)

# 디렉토리가 없으면 생성
os.makedirs(DB_DIR, exist_ok=True)

# 스레드 로컬 데이터베이스 연결
_local = threading.local()

def get_db_connection():
    """스레드에 안전한 데이터베이스 연결 가져오기"""
    if not hasattr(_local, 'conn'):
        _local.conn = sqlite3.connect(DB_PATH)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn

def close_db_connection():
    """데이터베이스 연결 닫기"""
    if hasattr(_local, 'conn'):
        _local.conn.close()
        del _local.conn

def initialize_db():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 파일 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        path TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        file_size INTEGER NOT NULL
    )
    ''')
    
    # 작업 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        error TEXT,
        FOREIGN KEY (file_id) REFERENCES files (id)
    )
    ''')
    
    # 분석 결과 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        results TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (file_id) REFERENCES files (id),
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    )
    ''')
    
    conn.commit()

# 데이터베이스 초기화
initialize_db()

def create_file_record(file_data):
    """파일 정보 저장"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # created_at을 문자열로 변환
    if isinstance(file_data["created_at"], datetime):
        file_data["created_at"] = file_data["created_at"].isoformat()
    
    cursor.execute(
        '''
        INSERT INTO files (id, filename, path, user_id, created_at, file_size)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            file_data["id"],
            file_data["filename"],
            file_data["path"],
            file_data["user_id"],
            file_data["created_at"],
            file_data["file_size"]
        )
    )
    
    # 작업 레코드 생성
    task_id = file_data.get("task_id", "task_" + file_data["id"])
    now = datetime.now().isoformat()
    
    cursor.execute(
        '''
        INSERT INTO tasks (id, file_id, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (task_id, file_data["id"], "pending", now, now)
    )
    
    conn.commit()
    return file_data["id"]

def get_file_info(file_id):
    """파일 정보 가져오기"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM files WHERE id = ?",
        (file_id,)
    )
    
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def update_task_status(task_id, status, error=None):
    """작업 상태 업데이트"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    if error:
        cursor.execute(
            '''
            UPDATE tasks
            SET status = ?, updated_at = ?, error = ?
            WHERE id = ?
            ''',
            (status, now, error, task_id)
        )
    else:
        cursor.execute(
            '''
            UPDATE tasks
            SET status = ?, updated_at = ?
            WHERE id = ?
            ''',
            (status, now, task_id)
        )
    
    conn.commit()
    return True

def save_analysis_results(file_id, task_id, results):
    """분석 결과 저장"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    results_json = json.dumps(results)
    
    cursor.execute(
        '''
        INSERT INTO analysis_results (id, file_id, task_id, results, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (file_id + "_" + task_id, file_id, task_id, results_json, now)
    )
    
    conn.commit()
    return True

def get_task_status(task_id):
    """작업 상태 가져오기"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def get_analysis_results(task_id):
    """분석 결과 가져오기"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 먼저 작업 상태 확인
    task = get_task_status(task_id)
    if not task or task["status"] != "completed":
        return {"status": task["status"] if task else "not_found"}
    
    # 분석 결과 가져오기
    cursor.execute(
        "SELECT * FROM analysis_results WHERE task_id = ?",
        (task_id,)
    )
    
    row = cursor.fetchone()
    if row:
        result_dict = dict(row)
        # JSON 문자열을 파이썬 객체로 변환
        result_dict["results"] = json.loads(result_dict["results"])
        return {
            "status": "completed",
            "data": result_dict["results"]
        }
    
    return {"status": "error", "message": "결과를 찾을 수 없습니다"}