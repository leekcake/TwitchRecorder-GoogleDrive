import asyncio
import datetime
import glob
import os
import threading
from io import StringIO

from aiohttp.web import Request

from aiohttp import web

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Main

from checker import Checker

MAIN: 'Main'
APP: web.Application

statusHtm: str


def readAll(path):
    file = open(path, mode='r')
    all_of_it = file.read()
    file.close()
    return all_of_it


def getHTML():
    global APP, MAIN, statusHtm

    grabbed = glob.glob(f'output/**/*.mp4', recursive=True)
    total = 0
    for grab in grabbed:
        total += os.path.getsize(grab)
    result = statusHtm.replace('#USE_DISK#', str(total / (1024 * 1024 * 1024)) + " GB")
    result = result.replace('#UPDATE#', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    table = StringIO()
    checker: Checker
    for checker in MAIN.checkers:
        table.write('<tr><td align="left">')
        table.write(checker.username)
        table.write('</td><td align="left">')
        if checker.isLive:
            table.write('Online')
        else:
            table.write('Offline')
        table.write('</td><td align="left">')
        if checker.isLive:
            table.write(checker.recorder.startedTime)
        else:
            table.write("NA")
        table.write('</td></tr>')

    return result.replace("#TABLE_ROW#", table.getvalue())

async def status(request: Request):
    return web.Response(body=getHTML(), content_type="text/html")


def launch(main):
    global APP, MAIN, statusHtm

    APP = web.Application()
    MAIN = main

    statusHtm = readAll('res/status.htm')
    #t = threading.Thread(target=run_server, args=(aiohttp_server(main),))
    #t.start()


def run_server(runner):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '127.0.0.1', 13939)
    loop.run_until_complete(site.start())
    loop.run_forever()


def aiohttp_server(main):
    global APP, MAIN, statusHtm

    APP = web.Application()
    MAIN = main

    statusHtm = readAll('res/status.htm')

    APP.add_routes([
        web.get("/", status),
        web.get('/status', status)
    ])

    runner = web.AppRunner(APP)
    return runner
