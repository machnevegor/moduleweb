from moduleweb import web

router = web.Router([
    web.template("static")
])


@router.error
async def error(request):
    return web.render("static/error.html")
