import os
from dotenv import load_dotenv



class Config:
  SECRET_KEY = ";pH93?hNSdT'O(D*e6SpOsE&}W%=["


class DevelopmentConfig(Config):
  load_dotenv()
  DEBUG=True
  MYSQLHOST = os.getenv("DB_HOST")
  MYSQL_USER = os.getenv("DB_USER")
  MYSQL_PASSWORD = os.getenv("DB_PASSWORD")
  MYSQL_DB = "proyectoPa"  

config = {
  "development": DevelopmentConfig
}