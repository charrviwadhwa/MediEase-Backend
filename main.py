from urllib.parse import unquote
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from utils import database
from utils.logger import Logger
#from fastapi.staticfiles import StaticFiles



app = FastAPI()
logger = Logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#pp.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def root():
    return {"status": "Api Is Running"}


@app.post("/api/auth")
async def api_auth(request: Request):
    data: dict = await request.json()
    logger.info(f"Auth Data: {data}")

    request_type = data.get("request_type")
    if not request_type:
        return {"status": False, "message": "Request type is required"}

    email = data.get("email", "").strip()
    if not email:
        return {"status": False, "message": "Email is required"}

    password = data.get("password", "").strip() if "password" in data else None


    if request_type == "new_auth":
        results = await database.new_auth(email, data)
    elif request_type == "check_auth":
        results = await database.check_auth(email, password)
    elif request_type == "check_account_type":
        results = await database.check_account_type(email)

    return results



# async def api_shops(request: Request):
    data: dict = await request.json()
    logger.info(f"Shops Data: {data}")

    request_type: Literal["get_shops"] = data.get("request_type")

    # medicine_name = data.get("medicine_name")
    # medicine_name = unquote(medicine_name)

    medicine_name = data.get("medicine_name", "").strip()
    if not medicine_name:
        return {"status": False, "message": "Medicine name is required"}

    medicine_name = unquote(medicine_name)

    user_location = data.get("user_location")
    if not user_location or not isinstance(user_location, dict):
        return {"status": False, "message": "User location is missing or invalid"}
    

    user_location = data.get("user_location")

    if request_type == "get_shops":
        results = await database.get_shops(medicine_name, user_location)

    return results
@app.post("/api/shops")
async def api_shops(request: Request):
    data: dict = await request.json()
    logger.info(f"Shops Data: {data}")

    request_type = data.get("request_type", "").strip()
    if request_type != "get_shops":
        return {"status": False, "message": "Invalid request type"}

    # ✅ Ensure medicine_name is assigned a value
    medicine_name = data.get("medicine_name", "")
    if not medicine_name:
        return {"status": False, "message": "Medicine name is required"}

    medicine_name = unquote(medicine_name.strip())  # ✅ Now it's defined properly

    user_location = data.get("user_location")
    if not user_location or not isinstance(user_location, dict):
        return {"status": False, "message": "User location is missing or invalid"}

    # ✅ Call database function only if all values are valid
    results = await database.get_shops(medicine_name, user_location)
    return results


# @app.post("/api/medicine")
# async def api_med(request: Request):
    data: dict = await request.json()
    logger.info(f"Med_data: {data}")

    request_type: Literal["update_med", "get_med", "add_med","delete_med"] = data.get("request_type")
    email = data.get("email", "").strip()
    if not email:
        return {"status": False, "message": "Email is required"}

    Med_data = data.get("Med_data", {})
    if not isinstance(Med_data, dict) or not Med_data:
        return {"status": False, "message": "Medicine data is missing or invalid"}


    if request_type == "add_med":
        results = await database.add_medicine(email, Med_data)

    elif request_type == "update_med":
        results = await database.update_medicine(email, Med_data)
    elif request_type == "get_med":
        results = await database.get_medicines(email)
    elif request_type == "get_all_med":
        results = await database.get_all_medicine()

    elif request_type == "delete_med":
        results = await database.delete_medicine(email,data.get('id'))

    return results

@app.post("/api/medicine")
async def api_med(request: Request):
    data: dict = await request.json()
    logger.info(f"Med_data: {data}")

    request_type = data.get("request_type")
    if not request_type:
        return {"status": False, "message": "Request type is required"}

    # ✅ Only require email for certain operations
    if request_type in ["add_med", "update_med", "delete_med"]:
        email = data.get("email", "").strip()
        if not email:
            return {"status": False, "message": "Email is required"}
    
    if request_type == "add_med":
        results = await database.add_medicine(email, data.get("Med_data", {}))

    elif request_type == "update_med":
        results = await database.update_medicine(email, data.get("Med_data", {}))

    elif request_type == "get_med":
        email = data.get("email", "").strip()  # ✅ Require email only for user medicines
        results = await database.get_medicines(email)

    elif request_type == "get_all_med":
        results = await database.get_all_medicine()  # ✅ No email required here

    elif request_type == "delete_med":
        results = await database.delete_medicine(email, data.get('id'))

    return results


@app.post("/api/buy")
async def api_buy(request: Request):
    data: dict = await request.json()
    logger.info(f"Med_data: {data}")

    request_type: Literal["buy_med"] = data.get("request_type")
    email = data.get("email", "").strip()
    if not email:
        return {"status": False, "message": "Email is required"}

    medicine_id = data.get("medicine_id")
    if medicine_id is None:
        return {"status": False, "message": "Medicine ID is required"}

    sold_quantity = data.get("sold_quantity")
    if sold_quantity is None or sold_quantity <= 0:
        return {"status": False, "message": "Invalid quantity"}


    if request_type == "buy_med":
        results = await database.buy_medicines(email, medicine_id, sold_quantity)
    return results
