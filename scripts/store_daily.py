import os
from datetime import timedelta, datetime
from typing import Optional
from pydantic import BaseModel
import requests


class Pocketbase:
    def __init__(self, base_url: str, identity: str, password: str):
        self.base_url = base_url
        self.identity = identity
        self.password = password
        self.user_token = None

    def authenticate(self):
        """
        Authenticate the user with the Pocketbase API.
        """
        url = f"{self.base_url}/api/admins/auth-with-password"
        payload = {"identity": self.identity, "password": self.password}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            self.user_token = response_data.get("token")
            print("Authentication successful")
        else:
            print("Authentication failed")
            print("Status code:", response.status_code)
            print("Response:", response.text)

    def insert_data(self, path: str, data: dict):
        """
        Insert data into Pocketbase.
        """
        if not self.user_token:
            print("User not authenticated. Please authenticate first.")
            return

        url = f"{self.base_url}{path}"
        headers = {"Authorization": self.user_token}
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print("Insertion successful")
            print(response.json())
        else:
            print("Insertion failed")
            print("Status code:", response.status_code)
            print("Response:", response.text)


class PocketbaseConfig:
    def __init__(self) -> None:
        self.base_url: str = os.getenv("POCKETBASE_URL"),
        self.identity: str = os.getenv("POCKETBASE_ADMIN_IDENTITY"),
        self.password: str = os.getenv("POCKETBASE_ADMIN_PASSWORD")

        print(vars(self))
    
    def __setattr__(self, name, value):
        if isinstance(value, tuple):
            # If value is a tuple, extract the inner string
            value = value[0]  # Assuming the tuple contains only one element
        super().__setattr__(name, value)
    
    
    


if __name__ == "__main__":
    # Load configuration from environment variables
    config = PocketbaseConfig()
    print(config.base_url)
    print(config.identity)
    print(config.password)

    # Initialize Pocketbase instance with configuration
    pocketbase = Pocketbase(
        base_url=config.base_url,
        identity=config.identity,
        password=config.password,
    )

    # Authenticate user
    pocketbase.authenticate()

    # Fetch data from Kraken API (I've kept this part outside the class)
    interval = 60  # in minutes
    since = datetime.now() - timedelta(days=1)
    since = since.timestamp()

    symbols = [
        "BTC/USDT",
        "LTC/USDT",
        "SOL/USDT"
    ]


    symbol = "BTC/USD"
    resp = requests.get(
        f'https://api.kraken.com/0/public/OHLC?pair={symbol}&interval={interval}&since={since}'
    )
    if resp.status_code == 200:
        result = resp.json().get("result", {}).get(symbol, [])
    else:
        print("Error fetching data from Kraken API")
        result = []

    # Insert fetched data into Pocketbase
    path = "/api/collections/btc_ohlc/records"
    for r in result:
        data = {
            "time": int(r[0]),
            "open": float(r[1]),
            "high": float(r[2]),
            "low": float(r[3]),
            "close": float(r[4]),
            "vmap": str(r[5]),
            "volume": float(r[6]),
            "count": int(r[7]),
        }
        pocketbase.insert_data(path, data)
