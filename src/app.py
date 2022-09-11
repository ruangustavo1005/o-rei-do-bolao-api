from fastapi import FastAPI
import src.status as status

app = FastAPI()

@app.get('/')
def root():
  return status.run()

@app.get('/status')
def status():
  return status.run()