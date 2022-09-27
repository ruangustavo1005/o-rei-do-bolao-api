from fastapi import FastAPI
from src import status, pontuacao

app = FastAPI()

@app.get('/')
def root():
  return status.run()

@app.get('/status')
def status():
  return status.run()

@app.get('/pontuacao/{camera_numero}')
async def pontuacao(camera_numero: int):
  return await pontuacao.run(camera_numero)

# @app.get('/config')
# def config():
#   connection = src.db.getConnection().cursor()
#   connection.execute("""
# SELECT *
#   FROM percent_match_config
#  WHERE cancha IS NULL
#    AND pino IS NULL;
# """)
#   return connection.fetchone();