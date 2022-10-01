from fastapi import FastAPI, Response
from src.status import run as status
from src.pontuacao import run as pontuacao

app = FastAPI()

@app.get('/')
def root_():
  return status()

@app.get('/status')
def status_():
  return status()

@app.get('/pontuacao/{camera_numero}')
async def pontuacao_(camera_numero: int, response: Response):
  return await pontuacao(camera_numero, response)
