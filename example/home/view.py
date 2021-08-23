from moduleweb import web

router = web.Router([
    web.preroute("/examples"),
    web.template("home")
])


@router.get("/")
async def home(request):
    return web.response("Hello, web!")


@router.get("~/str")
async def str(request):
    return web.response("String response")


@router.get("~/json")
async def json(request):
    return web.response({"response": "json"})


@router.get("~/redirect")
async def redirect(request):
    return web.redirect("https://github.com/machnevegor/ModuleWeb")


@router.get("~/render")
async def render(request):
    return web.render("home/index.html", {
        "query_set": dict(request.query)
    })
