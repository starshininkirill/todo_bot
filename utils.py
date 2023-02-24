import sqlite3


def update_task_status(db_name, t_id):
    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        db.execute(f"UPDATE test SET task_status=1 WHERE id={t_id}")


def delete_task_by_id(db_name, t_id):
    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM test WHERE id = {t_id}")


def add_task_to_db(db_name, uid, message):
    try:
        with sqlite3.connect(db_name) as db:
            cursor = db.cursor()
            cursor.execute(f"INSERT INTO test(user_id, task, task_status) VALUES ('{uid}', '{message}', 0)")
            return True
    except Exception:
        return False


def get_completed_tasks_by_uid(db_name, uid):
    all_task = []
    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        all_task_tuple = cursor.execute(
            f"SELECT id,user_id, task, task_status FROM test WHERE user_id = {uid} AND task_status=1")
        for task in all_task_tuple.fetchall():
            all_task.append({
                'task_id': task[0],
                'user_id': task[1],
                'task': task[2],
                'task_status': task[3]
            })
    return all_task


def get_tasks_by_uid(db_name, uid):
    all_task = []
    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        all_task_tuple = cursor.execute(f"SELECT id,user_id, task, task_status FROM test WHERE user_id = {uid} AND task_status=0")
        for task in all_task_tuple.fetchall():
            all_task.append({
                'task_id': task[0],
                'user_id': task[1],
                'task': task[2],
                'task_status': task[3]
            })
    print(len(all_task))
    return all_task