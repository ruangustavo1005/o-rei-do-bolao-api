import os
# carregando as environments do .env
from src import env
import uvicorn

# usado pra setar a porta
if __name__ == '__main__':
  uvicorn.run("src.app:app",
    host = "0.0.0.0",
    port = int(os.getenv('APP_PORT')),
    reload = bool(os.getenv('APP_RELOAD_ON_SAVE'))
  )
