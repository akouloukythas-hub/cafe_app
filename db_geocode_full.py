import sqlite3
import requests
import time

DB = "C:\\Users\\ANGY\\Downloads\\cafe_app\\cafe.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

# Επιλογή όλων των delivery παραγγελιών χωρίς lat/lng
c.execute("SELECT id, customer_name, address FROM orders WHERE type='delivery' AND (lat IS NULL OR lng IS NULL)")
rows = c.fetchall()

print(f"Βρέθηκαν {len(rows)} παραγγελίες χωρίς γεωκωδικοποίηση.")

for r in rows:
    order_id, customer_name, address = r
    print(f"Processing order {order_id} ({customer_name}): {address}")

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        response = requests.get(url, params=params, headers={"User-Agent": "CafeApp/1.0"})
        data = response.json()

        if len(data) > 0:
            lat = float(data[0]["lat"])
            lng = float(data[0]["lon"])
            print(f"  -> Found: lat={lat}, lng={lng}")
            c.execute("UPDATE orders SET lat=?, lng=? WHERE id=?", (lat, lng, order_id))
            conn.commit()
        else:
            print("  -> Δεν βρέθηκαν συντεταγμένες. Έλεγξε τη διεύθυνση.")

        time.sleep(1)  # Προστασία από rate limit

    except requests.exceptions.RequestException as e:
        print(f"  -> Network error: {e}. Προχωράμε στην επόμενη παραγγελία.")

    except Exception as e:
        print(f"  -> Άλλο σφάλμα: {e}. Προχωράμε στην επόμενη παραγγελία.")

# Εμφάνιση συνολικών stats
c.execute("SELECT COUNT(*) FROM orders WHERE type='delivery'")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM orders WHERE type='delivery' AND lat IS NOT NULL AND lng IS NOT NULL")
geocoded = c.fetchone()[0]
pending = total - geocoded

print("\n=== Summary ===")
print(f"Σύνολο delivery: {total}")
print(f"Geocoded: {geocoded}")
print(f"Pending: {pending}")

conn.close()
print("Geocoding complete! Το delivery_map θα δείχνει τώρα όλα τα markers.")
