from math import gcd
from fastapi import Response, status
from fastapi.responses import JSONResponse
import src.db as db
import numpy
import cv2

DIMENSAO_MAXIMA_ACEITA = 800
QUANTIDADE_TOTAL_PINOS = 9

async def run(camera_numero: int, response: Response):
  if (camera_numero < 1 or camera_numero > 4):
    response.status_code = status.HTTP_400_BAD_REQUEST
    return "número da câmera informado inválido"

  configuracoes_pinos = await get_config_pinos(camera_numero)

  if (len(configuracoes_pinos) < QUANTIDADE_TOTAL_PINOS):
    response.status_code = status.HTTP_428_PRECONDITION_REQUIRED
    return "é necessário configurar uma agulha para cada pino da camera %s antes de consultar a pontuação" % (camera_numero)
  
  imagemBase = cv2.imread('cancha.png', cv2.IMREAD_GRAYSCALE)
  if (camera_numero == 1):
    imagemBase = cv2.imread('cancha-1_.jpg', cv2.IMREAD_GRAYSCALE)
  elif (camera_numero == 2):
    imagemBase = cv2.imread('cancha-2_.jpg', cv2.IMREAD_GRAYSCALE)

  imagem = await redimensiona_mantendo_proporcoes(imagemBase)
  quantidade_pinos_levantados = await contabiliza_pinos(imagem, configuracoes_pinos)

  return QUANTIDADE_TOTAL_PINOS - quantidade_pinos_levantados

async def contabiliza_pinos(imagem, configuracoes_pinos):
  retangulos = []

  for (agulha, x_agulha, y_agulha, margem_erro, percentual_match) in configuracoes_pinos:
    match = cv2.matchTemplate(imagem, agulha, cv2.TM_CCOEFF_NORMED)
    
    height_agulha, width_agulha = agulha.shape
    height_agulha, width_agulha = (int(height_agulha), int(width_agulha))

    x_maximo = x_agulha + margem_erro
    x_minimo = x_agulha - margem_erro
    y_maximo = y_agulha + margem_erro
    y_minimo = y_agulha - margem_erro

    y_loc, x_loc = numpy.where(match >= percentual_match)
    for (x, y) in zip(x_loc, y_loc):
      x, y = (int(x), int(y))
      if ((x >= x_minimo and x <= x_maximo) or (y >= y_minimo and y <= y_maximo)):
        retangulos.append([x, y, width_agulha, height_agulha])

  retangulos_agrupados = cv2.groupRectangles(retangulos, 1)

  for (x, y, wei, hei) in retangulos_agrupados[0]:
    cv2.rectangle(imagem, (x, y), (x + wei, y + hei), (255, 0, 0,), 2)

  cv2.imshow('imagem', imagem)
  cv2.waitKey()
  cv2.destroyAllWindows()

  return len(retangulos_agrupados[0])

async def redimensiona_mantendo_proporcoes(imagem_original):
  originalHeight, originalWidth = imagem_original.shape
  maxDimensao = numpy.max([originalHeight, originalWidth])
  
  if (maxDimensao > DIMENSAO_MAXIMA_ACEITA):
    mdc = numpy.gcd(originalWidth, originalHeight)
    fatorMultiplicacao = DIMENSAO_MAXIMA_ACEITA / (maxDimensao / mdc)
    targetWidth = int(originalWidth  / mdc * fatorMultiplicacao)
    targetHeight = int(originalHeight / mdc * fatorMultiplicacao)
    
    return cv2.resize(imagem_original, (targetWidth, targetHeight))
  
  return imagem_original

async def get_config_pinos(camera_numero: int):
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
    percentual_match = percentual_match / 100
    results.insert(numero, [imagem, x, y, margem_erro, percentual_match])
    fetch = query.fetchone()

  return results