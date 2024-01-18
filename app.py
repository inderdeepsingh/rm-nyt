from datetime import date, timedelta
import functools
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import pyvips
import requests

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

# we are fetching nytimes frontpage, force the timezone
# to be new york timezone
os.environ["TZ"] = "America/New_York"


class FetchError(Exception):
    def __init__(self, msg, status_code):
        super().__init__(msg)
        self.msg = msg
        self.status_code = status_code

    def __str__(self):
        return f"FetchError({self.status_code}): {self.msg}"


app = FastAPI()


@functools.lru_cache(maxsize=5)
def get_image(dt):
    d = dt.isoformat().replace("-", "/")
    logger.info(f"fetching nytimes frontpage for {d}")
    i = pyvips.enums.Interesting()
    url = f"https://static01.nyt.com/images/{d}/nytfrontpage/scan.pdf"
    response = requests.get(url)
    if not response.ok:
        logger.warn(
            f"failed to fetch image for {d}: {response.status_code} {response.text}"
        )
        raise FetchError(
            f"failed to fetch image: {response.text}", response.status_code
        )
    logger.info(f"successfully fetched nytimes frontpage for {d}")
    pdf_buff = pyvips.Image.pdfload_buffer(response.content, dpi=300)
    img = pdf_buff.thumbnail_image(1404, height=1872, crop=i.LOW)
    img = img.write_to_buffer(".png")
    logger.info(f"successfully generated image from pdf for {d}")
    return img


@app.get("/today")
async def today():
    image = None
    d = date.today()
    d = d + timedelta(days=1)
    try:
        try:
            image = get_image(d)
        except FetchError as fe:
            if fe.status_code == 403:
                image = get_image(d - timedelta(days=1))
            else:
                raise fe
    except Exception as e:
        logger.exception("failed to generate image")
        raise HTTPException(status_code=500, detail=f"failed to generate image: {e}")
    return Response(content=image, media_type="image/png")
