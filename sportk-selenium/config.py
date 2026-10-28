import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
API_URL = os.getenv("API_URL", "http://localhost:3001")
BROWSER = os.getenv("BROWSER", "chrome")        # chrome | firefox | edge
HEADLESS = os.getenv("HEADLESS", "0") == "1"
TIMEOUT = 10                                    # giây, cho WebDriverWait

USER = {"email": "test@example.com", "password": "123456"}
