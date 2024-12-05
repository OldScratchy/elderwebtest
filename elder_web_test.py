import httpx
import time
import json
import logging
import sys
import datetime
import os
from logging.handlers import TimedRotatingFileHandler

APP_NAME = "ElderWebTest"
VERSION = "0.2411.2103"
DESCRIPTION = "Script para consultar URLs y loguear resultados."

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

LOG_DIR = "/fluent-bit/logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# log_filename = os.path.join(LOG_DIR, "web_checks.log")
# handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
# handler.suffix = "%Y-%m-%d"
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.addHandler(handler)
# formatter = logging.Formatter('%(message)s')
# handler.setFormatter(formatter)

def verificar_urls(urls, max_reintentos=3, timeout=10):
    resultados = []
    for url in urls:
        reintentos = 0
        while reintentos < max_reintentos:
            try:
                inicio = time.time()
                headers = {"User-Agent": "Bring your UA here"}
                with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout) as cliente:
                    respuesta = cliente.get(url)
                tiempo_respuesta = round(time.time() - inicio, 3)
                codigo_estado = respuesta.status_code
                motivo_redireccion = None
                url_final = respuesta.url

                if respuesta.history:
                    motivo_redireccion = respuesta.history[0].headers.get('Location', 'Desconocido')

                resultado = {
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "url": url,
                    "final_url": str(url_final),
                    "status_code": codigo_estado,
                    "response_time": tiempo_respuesta,
                    "success": True,
                    "error": None,
                    "retries": reintentos,
                    "redirect_reason": motivo_redireccion
                }
                break
            except httpx.RequestError as e:
                reintentos += 1
                if reintentos >= max_reintentos:
                    resultado = {
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "url": url,
                        "status_code": None,
                        "response_time": None,
                        "success": False,
                        "error": str(e),
                        "retries": reintentos,
                        "redirect_reason": None
                    }
                else:
                    time.sleep(1)
                    continue
        resultados.append(resultado)
    return resultados

def elder_web_test():
    urls = [
        "Define",
        "your",
        "own",
        "list",
        "of",
        "URLs",
        "here"
    ]

    resultados = verificar_urls(urls)
    for resultado in resultados:
        json_resultado = json.dumps(resultado)
        logger.info(json_resultado)

    eliminar_logs_antiguos(LOG_DIR, days=7)

def eliminar_logs_antiguos(directory, days=7):
    now = time.time()
    for filename in os.listdir(directory):
        if filename.startswith("web_tests.log"):
            filepath = os.path.join(directory, filename)
            if os.stat(filepath).st_mtime < now - days * 86400:
                os.remove(filepath)

if __name__ == "__main__":
    hi = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "app": APP_NAME,
        "version": VERSION,
        "whoami": DESCRIPTION
    }
    ini = json.dumps(hi)
    logger.info(ini)
    try:
        elder_web_test()
    except Exception as e:
        logger.error(json.dumps({
            "error": "Oups.",
            "exception": str(e)
        }))
        sys.exit(1)
