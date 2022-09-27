import json
import src.db as db
import numpy
import cv2

async def run(camera_numero: int):
  configuracoesPinos = await getConfigPinos(camera_numero)
  
  return configuracoesPinos

async def getConfigPinos(camera_numero: int):
  query = db.getConnection().cursor()
  query.execute("""
SELECT pin.numero,
       pin.pos_x AS x,
       pin.pos_y AS y,
       CASE WHEN pin.margem_erro_localizacao IS NOT NULL AND pin.margem_erro_localizacao > 0 THEN pin.margem_erro_localizacao
            WHEN cam.margem_erro_localizacao IS NOT NULL AND cam.margem_erro_localizacao > 0 THEN cam.margem_erro_localizacao
            WHEN ger.margem_erro_localizacao IS NOT NULL AND ger.margem_erro_localizacao > 0 THEN ger.margem_erro_localizacao
            ELSE 0
        END AS margem_erro_localizacao,
       CASE WHEN pin.percentual_match IS NOT NULL AND pin.percentual_match > 0 THEN pin.percentual_match
            WHEN cam.percentual_match IS NOT NULL AND cam.percentual_match > 0 THEN cam.percentual_match
            WHEN ger.percentual_match IS NOT NULL AND ger.percentual_match > 0 THEN ger.percentual_match
            ELSE 0
        END AS percentual_match,
       pin.imagem
  FROM configuracao_pino pin
  JOIN configuracao_camera cam
    ON cam.numero = pin.numero_camera
  JOIN configuracao ger
    ON ger.id = 1
 WHERE cam.numero = %s
 ORDER BY pin.numero
""", [camera_numero])

  results = []
  fetch = query.fetchone()
  while fetch:
    numero, x, y, margem_erro, percentual_match, imagem = fetch
    imagem = cv2.imdecode(numpy.asarray(bytearray(imagem), dtype=numpy.uint8), cv2.IMREAD_GRAYSCALE)
    results.insert(numero, [imagem, x, y, margem_erro, percentual_match])
    fetch = query.fetchone()

  return results