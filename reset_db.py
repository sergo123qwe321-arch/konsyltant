import sqlite3

def reset_db():
    conn = sqlite3.connect("konsyltant.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient_access WHERE gdrive_folder_id LIKE '%Павлик Морозов%' OR gdrive_folder_id LIKE '%Морозов%'")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"[DB RESET] Успешно удалено записей для папки Павлика Морозова: {deleted}")

if __name__ == "__main__":
    reset_db()
