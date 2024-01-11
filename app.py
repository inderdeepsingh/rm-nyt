import datetime
import functools


from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import pyvips
import requests

app = FastAPI()

@functools.lru_cache(maxsize=5)
def get_image(d):
    i = pyvips.enums.Interesting()
    url = f"https://static01.nyt.com/images/{d}/nytfrontpage/scan.pdf"
    response = requests.get(url)
    pdf_buff = pyvips.Image.pdfload_buffer(response.content, dpi=300)
    img = pdf_buff.thumbnail_image(1404, height=1872, crop=i.LOW)
    return img.write_to_buffer(".png")

@app.get('/nyt')
async def nyt_image():
    try:
        d = datetime.date.today().isoformat().replace('-', '/')
        image = get_image(d)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="failed to generate image")
    return Response(content=image, media_type="image/png")
