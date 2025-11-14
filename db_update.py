import sqlite3

DB = "cafe.db"  # το όνομα της βάσης σου

conn = sqlite3.connect(DB)
c = conn.cursor()

# Προσθήκη νέων πεδίων lat και lng
c.execute("ALTER TABLE orders ADD COLUMN lat REAL;")
c.execute("ALTER TABLE orders ADD COLUMN lng REAL;")

conn.commit()
conn.close()

print("Columns lat και lng προστέθηκαν στην orders.")
