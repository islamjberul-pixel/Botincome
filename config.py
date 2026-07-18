import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7602082599 # তোমার ID
DATABASE_URL = os.getenv("DATABASE_URL") # Railway Auto দিবে

WALLET_ADDRESS = "0xdcdB5EB1C3621Af39E6580e318dAC4615ae28989"
ACTIVATION_FEE = 0.15
LEVELS = [0.25, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
