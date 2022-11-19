import interactions
from fastapi import APIRouter, Request,Form
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse
from fastapi.templating import Jinja2Templates

from models.datastorage import ExampleData

from utils.commands import PrintableCommand, gather_all_commands
from utils.logger import get_logger,log_file_name
logger = get_logger()

templates = Jinja2Templates(directory="templates")

router = APIRouter()

client:interactions.Client = None  # type: ignore

@router.get("/home/example", response_class=HTMLResponse)
async def get_commands_page(request: Request):
    data = ExampleData.get_all(int(client.guilds[0].id))
    return templates.TemplateResponse("example.html", {"request": request, 'data': data})

@router.post("/home/example/delete",response_class=HTMLResponse)
async def delete_example(request: Request,id:int = Form()):
    ExampleData.delete(int(client.guilds[0].id),id)
    data = ExampleData.get_all(int(client.guilds[0].id))
    return templates.TemplateResponse("example.html", {"request": request, 'data': data})

@router.post("/home/example",response_class=HTMLResponse)
async def post_example(request: Request,textvalue:str = Form(),numbervalue:int = Form()):
    ExampleData.create(int(client.guilds[0].id),textvalue,numbervalue)
    data = ExampleData.get_all(int(client.guilds[0].id))
    return templates.TemplateResponse("example.html", {"request": request, 'data': data})
