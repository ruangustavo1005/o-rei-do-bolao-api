import psycopg2
import os

connection = psycopg2.connect("host=%s port=%s dbname=%s user=%s password=%s" % (
  os.getenv('DB_HOST'),
  os.getenv('DB_PORT'),
  os.getenv('DB_NAME'),
  os.getenv('DB_USER'),
  os.getenv('DB_PASS')
))

def getConnection():
  return connection