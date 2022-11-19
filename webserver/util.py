import interactions
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse
from fastapi.templating import Jinja2Templates

from utils.commands import PrintableCommand, gather_all_commands
from utils.logger import get_logger,log_file_name
logger = get_logger()

templates = Jinja2Templates(directory="templates")

router = APIRouter()

client:interactions.Client = None  # type: ignore

favicon_path = 'favicon.ico'

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@router.get("/",response_class=RedirectResponse)
async def home():
    return RedirectResponse(url="/home")

@router.get("/home", response_class=HTMLResponse)
async def get_home_page(request: Request):
    sub_pages = [
        ('/home/commands', 'Commands Übersicht'),
        ('/home/logs', 'logs'),
        ('/home/example', 'example'),
    ]
    return templates.TemplateResponse("index.html", {"request": request, 'sub_pages': sub_pages})

@router.get("/home/commands", response_class=HTMLResponse)
async def get_commands_page(request: Request):
    commands = gather_all_commands(client)
    return templates.TemplateResponse("commands.html", {"request": request, 'commands': commands})


@router.get("/home/logs",response_class=HTMLResponse)
async def fastapi_logs(request: Request):
    logger.handlers[0].flush()
    with open(log_file_name, 'r') as f:
        logs = f.readlines()
    logs_with_level = [(line.split('-')[3].strip().lower(),line) for line in logs]
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs_with_level})
