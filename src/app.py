from fastapi import FastAPI
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
async def pontuacao(camera_numero: int):
  return await src.pontuacao.run(camera_numero)

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