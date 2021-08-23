from moduleweb import web

app = web.App()

app.add([
    web.module("static"),
    web.module("home")
])

app.run()
