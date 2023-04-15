from fastapi import Response, status
import src.db as db
import numpy
import cv2

DIMENSAO_MAXIMA_ACEITA = 800
QUANTIDADE_TOTAL_PINOS = 9

async def run(cameraNumero: int, response: Response):
  if (cameraNumero < 1 or cameraNumero > 4):
    response.status_code = status.HTTP_400_BAD_REQUEST
    return "número da câmera informado inválido"

  configuracoesPinos = await getConfigPinos(cameraNumero)

  if (len(configuracoesPinos) < QUANTIDADE_TOTAL_PINOS):
    response.status_code = status.HTTP_428_PRECONDITION_REQUIRED
    return "é necessário configurar uma agulha para cada pino da camera %s antes de consultar a pontuação" % (cameraNumero)
  
  frame = False
  endpointRTSP = await getEndpointRtspCamera(cameraNumero)
  
  if endpointRTSP == '':
    response.status_code = status.HTTP_428_PRECONDITION_REQUIRED
    return "é necessário configurar o endpoint RTSP para a câmera %s" % (cameraNumero)
  
  cap = cv2.VideoCapture(endpointRTSP)
  if cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  else:
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return "não foi possível recuperar o vídeo da câmera %s pelo endpoint RTSP %s" % (cameraNumero, endpointRTSP)
  
  # imagemBase = cv2.imread('img/cancha.JPG', cv2.IMREAD_GRAYSCALE)
  # if (cameraNumero == 1):
  #   imagemBase = cv2.imread('img/cancha-1_.JPG', cv2.IMREAD_GRAYSCALE)
  # elif (cameraNumero == 2):
  #   imagemBase = cv2.imread('img/cancha-2_.JPG', cv2.IMREAD_GRAYSCALE)

  imagem = await redimensionaMantendoProporcoes(frame)
  quantidadePinosLevantados = await contabilizaPinos(imagem, configuracoesPinos)

  return QUANTIDADE_TOTAL_PINOS - quantidadePinosLevantados

async def contabilizaPinos(imagem, configuracoesPinos):
  retangulos = []

  for (agulha, xAgulha, yAgulha, margemErro, percentualMatch) in configuracoesPinos:
    match = cv2.matchTemplate(imagem, agulha, cv2.TM_CCOEFF_NORMED)
    
    heightAgulha, widthAgulha = agulha.shape
    heightAgulha, widthAgulha = (int(heightAgulha), int(widthAgulha))

    xMaximo = xAgulha + margemErro
    xMinimo = xAgulha - margemErro
    yMaximo = yAgulha + margemErro
    yMinimo = yAgulha - margemErro

    y_loc, x_loc = numpy.where(match >= percentualMatch)
    for (x, y) in zip(x_loc, y_loc):
      x, y = (int(x), int(y))
      if ((x >= xMinimo and x <= xMaximo) or (y >= yMinimo and y <= yMaximo)):
        retangulos.append([x, y, widthAgulha, heightAgulha])

  retangulos_agrupados = cv2.groupRectangles(retangulos, 1)

  # for (x, y, wei, hei) in retangulos_agrupados[0]:
  #   cv2.rectangle(imagem, (x, y), (x + wei, y + hei), (255, 0, 0,), 2)

  # cv2.imshow('imagem', imagem)
  # cv2.waitKey()
  # cv2.destroyAllWindows()

  return len(retangulos_agrupados[0])

async def redimensionaMantendoProporcoes(imagemOriginal):
  originalHeight, originalWidth = imagemOriginal.shape
  maxDimensao = numpy.max([originalHeight, originalWidth])
  
  if (maxDimensao > DIMENSAO_MAXIMA_ACEITA):
    mdc = numpy.gcd(originalWidth, originalHeight)
    fatorMultiplicacao = DIMENSAO_MAXIMA_ACEITA / (maxDimensao / mdc)
    targetWidth = int(originalWidth  / mdc * fatorMultiplicacao)
    targetHeight = int(originalHeight / mdc * fatorMultiplicacao)
    
    return cv2.resize(imagemOriginal, (targetWidth, targetHeight))
  
  return imagemOriginal

async def getConfigPinos(cameraNumero: int):
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
""", [cameraNumero])

  results = []
  fetch = query.fetchone()
  while fetch:
    numero, x, y, margemErro, percentualMatch, imagem = fetch
    imagem = cv2.imdecode(numpy.asarray(bytearray(imagem), dtype=numpy.uint8), cv2.IMREAD_GRAYSCALE)
    percentualMatch = percentualMatch / 100
    results.insert(numero, [imagem, x, y, margemErro, percentualMatch])
    fetch = query.fetchone()

  return results

async def getEndpointRtspCamera(cameraNumero: int):
  query = db.getConnection().cursor()
  query.execute("""
SELECT endpoint_rtsp
  FROM configuracao_camera
 WHERE numero = %s
""", [cameraNumero])

  endpoint_rtsp = ''
  fetch = query.fetchone()
  if fetch:
    endpoint_rtsp, = fetch

  return endpoint_rtsp