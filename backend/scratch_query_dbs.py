import os
import sqlite3

def query_dbs():
    for r, d, fs in os.walk('.'):
        if 'venv' in r or '.git' in r:
            continue
        for f in fs:
            if f.endswith('.db'):
                path = os.path.join(r, f)
                print(f"Database: {path} (Size: {os.path.getsize(path)} bytes)")
                try:
                    conn = sqlite3.connect(path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    print("  Tables:", tables)
                    for t in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {t}")
                        count = cursor.fetchone()[0]
                        print(f"    Table: {t} | Count: {count}")
                        cursor.execute(f"SELECT id, name, path, size, category FROM {t} LIMIT 100")
                        rows = cursor.fetchall()
                        print(f"    Sample rows ({len(rows)}):")
                        for r in rows:
                            print(f"      ID: {r[0]} | Name: {r[1]} | Path: {r[2]} | Size: {r[3]} | Category: {r[4]}")
                    conn.close()
                except Exception as e:
                    print(f"  Error querying {path}: {e}")

if __name__ == "__main__":
    query_dbs()
