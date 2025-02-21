import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal

from config1 import MONGODB_URL
from utils.logger import Logger

logger = Logger(__name__)
MONGODB_URL = "mongodb://127.0.0.1:27017/meditrack"
client = AsyncIOMotorClient(MONGODB_URL)

DB = client["meditrack"]
ACCOUNTDB = DB["ACCOUNTDB"]
logger.info("Connecting to MongoDB")
logger.info("Connected to MongoDB")



import math


def calculate_distance(lat1, lon1, lat2, lon2):
    print(lat1, lon1, lat2, lon2)
    R = 6371  # Radius of the Earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dLon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in kilometers
    return round(distance, 2)


# For Login Signup


async def new_auth(email: str, data):
    if await ACCOUNTDB.find_one({"email": email}):
        return {"status": False, "message": "Email already exists"}
    print(data)
    await ACCOUNTDB.insert_one(data)
    return {"status": True, "message": "Signup Successful"}


async def check_auth(email: str, password: str):
    user = await ACCOUNTDB.find_one({"email": email})
    if user:
        if user["password"] == password:
            return {"status": True, "message": "Login Successful"}
        return {"status": False, "message": "Incorrect Password"}

    return {"status": False, "message": "Email not found"}


async def check_account_type(email: str):
    acc = await ACCOUNTDB.find_one({"email": email})
    if acc:
        return {"status": True, "type": acc["type"]}
    return {"status": False, "message": "Email not found"}


# async def get_shops(medicine_name, user_location):

    shops = []
    async for shop in ACCOUNTDB.find({"type": "shop"}):
        shop.pop("_id")
        shop.pop("password")

        if shop.get("medicine", []) != []:
            for medicine in shop["medicine"]:
                if medicine["name"] == medicine_name:
                    data = {
                        "shop_name": shop["name"],
                        "shop_location": shop["location"],
                        "distance": calculate_distance(
                            float(user_location["lat"]),
                            float(user_location["long"]),
                            float(shop["location"]["lat"]),
                            float(shop["location"]["long"]),
                        ),
                        "price": medicine["price"],
                        "id": medicine["id"],
                        "shop_email": shop["email"],
                        "frequency": medicine["dosage"],
                        "sideeffect": medicine["side_effects"],
                        "precaution": medicine["precautions"],
                    }
                    shops.append(data)
                    break

    shops = sorted(shops, key=lambda x: x["distance"])

    return {"status": True, "shops": shops}

async def get_shops(medicine_name, user_location):
    shops = []
    async for shop in ACCOUNTDB.find({"type": "shop"}):
        shop.pop("_id", None)  # ✅ Prevent KeyError for missing "_id"

        # ✅ Skip shops that are missing a location
        if "location" not in shop or not isinstance(shop["location"], dict):
            print(f"❌ Skipping shop due to missing location: {shop}")
            continue

        shop_data = {
            "shop_name": shop.get("name", "Unknown Shop"),
            "shop_location": shop["location"],
            "distance": calculate_distance(
                float(user_location.get("lat", 0)),  # ✅ Default to 0 if missing
                float(user_location.get("long", 0)),
                float(shop["location"].get("lat", 0)),
                float(shop["location"].get("long", 0)),
            ),
            "directional_link": shop.get("directional_link", "N/A")  # ✅ Default value
        }
        shops.append(shop_data)

    return {"status": True, "shops": sorted(shops, key=lambda x: x["distance"])}


# For Account Details


async def update_account(email: str, data: dict):
    await ACCOUNTDB.update_one({"email": email}, {"$set": data}, upsert=True)
    return {"status": True, "message": "Account Updated"}


async def get_account(email: str):
    account = await ACCOUNTDB.find_one({"email": email})
    if account:
        return {"status": True, "data": account}

    return {"status": False, "message": "Email not found"}


# for medicinces


async def add_medicine(email: str, data: dict):
    await ACCOUNTDB.update_one(
        {"email": email}, {"$push": {"medicine": data}}, upsert=True
    )
    return {"status": True, "message": "Medicine added"}


async def update_medicine(email: str, data: dict):
    await ACCOUNTDB.update_one(
        {"email": email, "medicine.id": data["id"]},
        {"$set": {"medicine.$": data}},
        upsert=True,
    )
    return {"status": True, "message": "Medicine updated"}


async def get_medicines(email: str):
    shop_data = await ACCOUNTDB.find_one({"email": email})
    if shop_data:
        if shop_data.get("medicine", []) != []:
            return {"status": True, "medicine": shop_data["medicine"]}
    return {"status": True, "medicine": []}


async def buy_medicines(email: str, medicine_id: int, sold_quantity: int):
    print(email, medicine_id, sold_quantity)
    await ACCOUNTDB.update_one(
        {"email": email, "medicine.id": int(medicine_id)},
        {
            "$inc": {
                "medicine.$.quantity": (-1) * int(sold_quantity),
                "medicine.$.units_sold": int(sold_quantity),
            }
        },
        upsert=True,
    )
    return {"status": True, "message": "Medicine Sold"}


# async def get_all_medicine():
#     medicines = []
#     async for shop in ACCOUNTDB.find({"type": "shop"}):
#         print(shop)
#         if shop.get("medicine", []) != []:
#             for medicine in shop["medicine"]:
#                 medicines.append(medicine["name"])

#     return {"status": True, "medicines": list(set(medicines))}
async def get_all_medicine():
    medicines = []
    async for record in DB["medicines"].find({}, {"_id": 0}):  # ✅ Fetch all medicines
        medicines.append(record)
    
    return {"status": True, "medicines": medicines}



async def delete_medicine(email: str, id):
    print(id)
    await ACCOUNTDB.update_one({"email": email}, {"$pull": {"medicine": {"id": id}}})
    return {"status": True, "message": "Medicine Deleted"}
