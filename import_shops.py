import csv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# ✅ MongoDB Connection
MONGODB_URL = "mongodb://127.0.0.1:27017/"
client = AsyncIOMotorClient(MONGODB_URL)
DB = client["meditrack"]  # ✅ Your database
SHOPS_COLLECTION = DB["ACCOUNTDB"]  # ✅ Collection for shops

async def import_csv_to_mongo(csv_file):
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        shops = []

        for row in reader:
            # ✅ Skip rows with missing values
            if not row.get("Latitude") or not row.get("Longitude") or not row.get("Name"):
                print(f"❌ Skipping row due to missing data: {row}")
                continue

            try:
                shop = {
                    "name": row["Name"].strip(),
                    "type": "shop",  # ✅ Add "type" to filter in FastAPI
                    "location": {
                        "lat": float(row["Latitude"]),  # ✅ Ensures correct type
                        "long": float(row["Longitude"])
                    },
                    "directional_link": row.get("Directional link", "N/A")  # ✅ Avoid KeyError
                }
                shops.append(shop)
            except ValueError:
                print(f"❌ Skipping invalid row: {row}")
                continue

        if shops:
            await SHOPS_COLLECTION.insert_many(shops)
            print("✅ Shops inserted successfully!")
        else:
            print("⚠️ No valid shop data found to insert.")

# Run the import function
asyncio.run(import_csv_to_mongo("data/shops.csv"))  # ✅ Change this to your actual CSV file path
