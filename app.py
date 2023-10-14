from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import requests
from pydantic import BaseModel
import re
app = FastAPI()

templates = Jinja2Templates(directory="templates")


class Item(BaseModel):
    cardnum: str
    exp: str


@app.get("/", response_class=HTMLResponse)
async def read_card(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def post_card(request: Request, cname: str = Form(""), ex: str = Form("")):
    data_type = f"""
                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                    <GetCardType xmlns="http://localhost/SmartPayments/">
                    <CardNumber>{cname}</CardNumber>
                    </GetCardType>
                </soap12:Body>
                </soap12:Envelope>
                        """

    data_valid = f"""
                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                    <ValidCard xmlns="http://localhost/SmartPayments/">
                    <CardNumber>{cname}</CardNumber>
                    <ExpDate>{ex}</ExpDate>
                    </ValidCard>
                </soap12:Body>
                </soap12:Envelope>
                    """
    url = "https://secure.ftipgw.com/ArgoFire/validate.asmx?WSDL"
    headers = {'content-type': 'text/xml'}
    response_type = requests.post(url, data=data_type, headers=headers)
    res_type = re.search(
        "<GetCardTypeResult>(.*)</GetCardTypeResult>", response_type.text)
    response_valid = requests.post(url, data=data_valid, headers=headers)
    res_valid = re.search(
        "<ValidCardResult>(.*)</ValidCardResult>", response_valid.text)
    try:
        type_ = res_type.group(1)
    except Exception as e:
        type_ = "Not Found"
    return templates.TemplateResponse("home.html", {"request": request, "cname": type_, "ex": res_valid.group(1)})

if __name__ == '__main__':
    uvicorn.run("app:app",reload=True, port=5000, host="0.0.0.0")
