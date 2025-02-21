import csv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# ✅ MongoDB Connection
MONGODB_URL = "mongodb://127.0.0.1:27017/"
client = AsyncIOMotorClient(MONGODB_URL)
DB = client["meditrack"]  # ✅ Your database
MEDICINE_COLLECTION = DB["ACCOUNTDB"]  # ✅ Collection for medicines

async def import_medicines(csv_file):
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        medicines = []

        for row in reader:
            # ✅ Skip empty rows
            if not row.get("Name") or not row.get("Price (₹)"):
                print(f"❌ Skipping row due to missing data: {row}")
                continue

            try:
                medicine = {
                    "name": row["Name"].strip(),
                    "brand": row["Brand"].strip(),
                    "price": float(row["Price (₹)"]),
                    "side_effects": row.get("Side Effects", "N/A"),
                    "precautions": row.get("Precautions", "N/A"),
                    "dosage": row.get("Time", "As prescribed")
                }
                medicines.append(medicine)
            except ValueError:
                print(f"❌ Skipping invalid row: {row}")
                continue

        if medicines:
            await MEDICINE_COLLECTION.update_one(
                {"type": "medicines"},
                {"$set": {"medicine": medicines}},
                upsert=True
            )
            print("✅ Medicines inserted successfully!")
        else:
            print("⚠️ No valid medicine data found to insert.")

# Run the import function
asyncio.run(import_medicines("data/med.csv"))  # ✅ Change this to your actual CSV file path
