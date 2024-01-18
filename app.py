import datetime
import functools
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import pyvips
import requests

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

class FetchError(Exception):
    pass

app = FastAPI()

@functools.lru_cache(maxsize=5)
def get_image(d):
    logger.info(f"fetching nytimes frontpage for {d}")
    i = pyvips.enums.Interesting()
    url = f"https://static01.nyt.com/images/{d}/nytfrontpage/scan.pdf"
    response = requests.get(url)
    if not response.ok:
        raise FetchError(f"failed to fetch image: {response.status_code}")
    logger.info(f"successfully fetched nytimes frontpage for {d}")
    pdf_buff = pyvips.Image.pdfload_buffer(response.content, dpi=300)
    img = pdf_buff.thumbnail_image(1404, height=1872, crop=i.LOW)
    img = img.write_to_buffer(".png")
    logger.info(f"successfully generated image from pdf for {d}")
    return img

@app.get('/today')
async def today():
    try:
        d = datetime.date.today().isoformat().replace('-', '/')
        image = get_image(d)
    except Exception as e:
        logger.exception("failed to generate image")
        raise HTTPException(status_code=500, detail=f"failed to generate image: {e}")
    return Response(content=image, media_type="image/png")
