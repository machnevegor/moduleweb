# MEB | Docs for [ModuleWeb](https://pypi.org/project/moduleweb/) [v1.0]

## Introduction

> **[ModuleWeb](https://pypi.org/project/moduleweb/)** is a multi-purpose library that aims to speed up the development of web applications and make it convenient to route your project. **[ModuleWeb](https://pypi.org/project/moduleweb/)** is written in **[Python](https://www.python.org)** using the multifunctional **[Aiohttp](https://docs.aiohttp.org/en/stable/)** framework and the powerful **[Jinja2](https://jinja2docs.readthedocs.io/en/stable/)** template engine. With the help of **[ModuleWeb](https://pypi.org/project/moduleweb/)** tools, you can quickly and conveniently write highly loaded, easily scalable and, most importantly, asynchronous web applications. If you are new to programming, then do not worry, **[ModuleWeb](https://pypi.org/project/moduleweb/)** will be a good start in the web. Well, let's move on to the [Installation](#installation) and [Quickstart & Docs](#quickstart--docs)!

## Installation

To install this module in your **[Python](https://www.python.org)** project, you will need:

1. Have **[Python](https://www.python.org)** higher than or equal to version 3.7 on your device

2. Open the terminal and enter the following command:

```
pip install moduleweb
```

3. Now you can go to [Quickstart & Docs](#quickstart--docs) and write a web application

## Quickstart & Docs

#### File structure

> Before we start, I would like to note that **[ModuleWeb](https://pypi.org/project/moduleweb/)** is called so for a reason. A module in **[ModuleWeb](https://pypi.org/project/moduleweb/)** is a unit of your application that is designed to store a file with a router, a folder with your templates and a set of some separate logic. You don't need to write the entire application in one file, because this is wrong, instead get used to the good and divide everything into modules!

The file structure of an application written in **[ModuleWeb](https://pypi.org/project/moduleweb/)** can be absolutely any form. Here is an example of a regular file structure designed for a minimalistic web application:

```
my_first_app
├── static
│   ├── template
│   │   └── ...
│   └── view.py
├── home
│   ├── template
│   │   └── ...
│   └── view.py
└── main.py
```

> Experienced programmers will probably be surprised and say: is static also a module? In fact, the reason why this is done in this example is very simple: why do we need to make two separate folders for middlewares and static files, if they can be combined into one module. Don't worry, if you want a folder with static, and not a module, then you can also do this in **[ModuleWeb](https://pypi.org/project/moduleweb/)**!

---

#### Code for main.py

Now we are ready to go to main.py in the root of the application and write your first code:

```python
from moduleweb import web

app = web.App()

app.add([
    web.module("static"),
    web.module("home")
])

app.run()
```

I understand that this may seem difficult for some, but let's take everything in order:

- In the first line, we simply import the web from the **[ModuleWeb](https://pypi.org/project/moduleweb/)** library.
- In the next line, we will initialize the application. By the way, if you want to initialize the application in another file, namely a file that is not \_\_main\_\_, it is recommended to pass \_\_name\_\_ to web.App to avoid path and route conflicts when building a project and running it!
- Next comes the part that is a little more complicated than the previous ones, so let's analyze it in the next paragraph, but for now we will discuss the very end. The very last line indicates the start of the application launch. By default, your web application will start on localhost with port 8000. If you want to change the host or port, you will need to pass the host and port separately.

---

#### Static and module

> Before we talk about app.add, let's distinguish between the two concepts of route and path. Route is a concept for a browser string, and path is a local path in the project relative to something. This is important to distinguish, because route always starts with a slash at the very beginning.

The app.add method is used to add modules and statics to your application. To add the latter, you need to write the following code, passing the first parameter the route by which your folder will be accessible in the browser, and the second parameter the path in your application to the static folder and, very importantly, the path should be relative to the file where the web.App instance is located:

```python
app.add([
    web.static("/static", "path/to/your/static/folder")
])
```

To add modules, you need to write the following code and pass the first parameter to the path to the module and, very importantly, the path should be relative to the file where the web.App is located, and with the second optional parameter, you can pass the path already relative to the module where the router instance is located in it. Note that if you named the file and the variable with the router as in this [Quickstart & Docs](#quickstart--docs), then you do not need to specify the second parameter. In this example, I will specify everything, just in case, so that you will learn:

```python
app.add([
    web.module("path/to/your/module", "view.router")
])
```

> By the way, keep in mind that you can't just import a router using standard **[Python](https://www.python.org)** methods anywhere, as this can lead to errors, so always use web.module! However, if it is important for you to create an application in a single file, then you can inside main.py immediately write a router and then pass its instance to app.add — this is not a bug, but a feature😏

---

#### Routing file

Now we can start writing code in view.py, which is located in a module named home:

```python
from moduleweb import web

router = web.Router([
    web.template("home")
])

@router.get("/")
async def handler(request):
    return web.response("Hello, web!")
```

Let me tell you what each part of the code is responsible for, as I did earlier:

- In the first line, we also import web.
- Next, we initialize the router and pass the options you need to it. If you only need a router, then you can not transmit anything. We will return to the router options later...
- Then we use a special decorator based on the router instance to wrap the handler. This asynchronous handler will be called every time the route passed to the decorator is requested from the server. It is also important to note that there are two types of get and post requests in **[ModuleWeb](https://pypi.org/project/moduleweb/)**. At the very end of the handler, we must return some result. It is important to note that we can't just return, for example, a string. Your result must first pass a special method, for example, as web.response, but we will return to all methods later.

---

#### Router options

There are several options that you can add to the router, and each option can be added several times for different purposes. Let's start with the first and important option, which is called preroute. You can use it to shorten the length of each route that you will initialize using decorators. It is very simple to add it: the first mandatory parameter you need to pass the route, which will later be inserted automatically instead of briefly at the very beginning of the route, and the second, but no longer mandatory parameter itself is briefly (by default, the usual tilde). Let me show you how you can add preroute to the router options:

```python
router = web.Router([
    web.preroute("/home", "~")
])
```

It is important to know that all the preroutes in the router will only work for the same router, so you need to define your own preroutes for each router. This was done to avoid collisions. Let me show you how to use preroute in practice, only this time I will not specify the second optional parameter:

```python
router = web.Router([
    web.preroute("/blog")
])

@router.get("~/posts")
async def handler(request):
    ...

@router.get("~/comments")
async def handler(request):
    ...
```

Now let's talk about adding templates to your application. The trick is that you can add templates directly to the router, and, most interestingly, you do not need to specify the full path from the root directory of the application to the folder with templates. You just need to specify the name of your template as the first parameter that you want to access in the future to get all the components of this template. The second optional parameter can specify the path to the folder relative to the router, in which all the components are located. Here is an example of using it (here I will specify all the parameters, but it is not necessary to do this):

```python
router = web.Router([
    web.template("home", "template")
])
```

It is important to know that, unlike preroute, the template option applies to the entire application, so be more careful when choosing a template name to avoid name collisions. By the way, you can also access template elements in the browser by simply specifying the name of the required template as a route, but we'll talk about this a little later...

---

#### Types of responses

During the construction of the application, you will need to think about how your handlers will return data or how they will react. At the moment, there are three built-in response types in **[ModuleWeb](https://pypi.org/project/moduleweb/)** that are important to know about. The first type of response is quite primitive, it can return strings or JSON objects to the client, depending on what you pass to it: a dictionary or a string. Note that you can't just return a string or a dictionary at the very end of the handler: it is important to put them initially in web.response. Here is an example of using web.response to send a string or a JSON object to the client:

```python
@router.get("/str")
async def str_handler(request):
    return web.response("String response")

@router.get("/json")
async def json_handler(request):
    return web.response({"response": "json"})
```

The following type of response allows you to automatically redirect the client to another page. This type of answer is also primitive, so I also suggest taking a look at the example and moving on:

```python
@router.get("/redirect}")
async def redirect_handler(request):
    return web.redirect("/some/route/or/url")
```

And finally, let's move on to the most interesting type of response that is built into **[ModuleWeb](https://pypi.org/project/moduleweb/)**. This type of response has the name render. It is designed to process your template and its components using the built-in powerful **[Jinja2](https://jinja2docs.readthedocs.io/en/stable/)** template engine. To call the render, you need to pass the first mandatory parameter is entry point for the render, and the second, but already optional parameter, the context in the form of a dictionary, if it is in your template. Let's take a look at an example where there is no context (in the future there will be an example where there is a context):

```python
@router.get("/render}")
async def render_handler(request):
    return web.render("home/index.html")
```

> These are not the only ways to send a response to the client — you can use any libraries originally designed for **[Aiohttp](https://docs.aiohttp.org/en/stable/)**!

---

#### Template сomponents

It is worth talking a little more about templates and their components. First of all, I would like to say that you can arrange the component files inside any module template as you like. To interact with any component, you need to use the appropriate construction: the template name + the path from this template to the component you need. Here is an example of how you can render a template that has files with markup and styles:

```python
@router.get("/render")
async def render_handler(request):
    return web.render("home/index.html", {"query_set": dict(request.query)})
```

```html
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="home/styles.css" />
  </head>
  <body>
    <h1>
      {{ query_set }}
    </h1>
  </body>
</html>
```

```css
h1 {
  background-color: #000;
  color: #00f;
}
```

---

#### Middlewares and 404 handler

To add any middleware to your application, you will need to use a special decorator in the router:

```python
@router.middleware
async def middleware(request, handler):
    ...
```

By the way, if you want to add a middleware that handles an error that will be caused due to an incorrect route (error 404: the page was not found), then you do not need to write something with your hands, just use a special decorator that is provided in the router:

```python
@router.error
async def error(request):
    return web.render("static/error.html")
```

## Conclusion

> **[ModuleWeb](https://pypi.org/project/moduleweb/)** can be a good library for you to create web applications using the modular method, whether you are a beginner or a pro. The ability to write asynchronous code, use all known libraries designed for **[Aiohttp](https://docs.aiohttp.org/en/stable/)**, use the built-in **[Jinja2](https://jinja2docs.readthedocs.io/en/stable/)** engine, modular architecture, relative and at the same time fundamentally independent of the application file structure paths, the ability to add statics, a special 404 page handler, the ability to quickly write code using decorators, convenient default values, the preroute option for each router, a well-thought-out route system that solves the errors of other **[Python](https://www.python.org)** frameworks, and much more — isn't it a miracle?
