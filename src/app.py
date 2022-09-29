from fastapi import FastAPI, Response
import src.status
import src.pontuacao

app = FastAPI()

@app.get('/')
def root():
  return src.status.run()

@app.get('/status')
def status():
  return src.status.run()

@app.get('/pontuacao/{camera_numero}')
async def pontuacao(camera_numero: int, response: Response):
  return await src.pontuacao.run(camera_numero, response)
