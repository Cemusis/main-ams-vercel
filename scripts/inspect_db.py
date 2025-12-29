import sqlite3
import sys

DB = 'db.sqlite3'

con = sqlite3.connect(DB)
cur = con.cursor()

print('PRAGMA foreign_keys=')
cur.execute('PRAGMA foreign_keys')
print(cur.fetchone())

print('\nTables:')
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"): 
    print('-', row[0])

def show_schema(name):
    cur.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,))
    r = cur.fetchone()
    print(f"\nSchema for {name}:")
    print(r[0] if r else 'NOT FOUND')

for t in ('archive_record','physical_location','users','borrow_transaction','log'):
    show_schema(t)

print('\nArchive record columns:')
for r in cur.execute("PRAGMA table_info('archive_record')"):
    print(r)

print('\nCount rows:')
for t in ('archive_record','physical_location','users'):
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}:", cur.fetchone()[0])

print('\nDuplicate file_codes (if any):')
cur.execute("SELECT file_code, COUNT(*) as c FROM archive_record GROUP BY file_code HAVING c>1")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(r)
else:
    print('None')

print('\nSample physical_location rows:')
for r in cur.execute('SELECT location_id, shelf_number, bay_code, section_number, full_location_code FROM physical_location LIMIT 10'):
    print(r)

print('\nSample users (first 10):')
for r in cur.execute('SELECT email, full_name, role FROM users LIMIT 10'):
    print(r)

con.close()
