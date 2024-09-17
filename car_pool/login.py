from dataclasses import dataclass

from app import app
from auth import hash_password, verify_password
from db.init_db import load_database
from fasthtml.common import *

db = load_database()


@dataclass
class Credentials:
    name: str
    password: str


@app.get("/login")
def login_page():
    return Titled(
        "Login",
        Form(
            Input(id="name", placeholder="Name", name="name"),
            Input(
                id="password", type="password", placeholder="Password", name="password"
            ),
            Nav(
                Button("Login"),
                A("Create account", cls="secondary", href="/signup"),
                role="grid",
            ),
            action="/login",
            method="post",
        ),
        style="max-width: 300px;",
    )


@app.post("/login")
def login(credentials: Credentials, sess):
    users = load_database().t.users
    user = users.get(credentials.name)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    if not verify_password(user.password_salt, credentials.password):
        return RedirectResponse("/login", status_code=303)

    sess["auth"] = credentials.name
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
def get(sess):
    sess["auth"] = None
    return RedirectResponse("/", status_code=303)


@dataclass
class UserForm:
    name: str
    password: str


@app.get("/signup")
def signup_page():
    return Titled(
        "Create account",
        signup_form(UserForm(name=None, password=None)),
        style="max-width: 300px;",
    )


def signup_form(user: UserForm, error=""):
    return Form(
        Input(
            id="username",
            placeholder="username",
            value=user.name,
            name="name",
            hx_post="/signup/validate",
            hx_trigger="input changed",
            hx_swap="inner_html",
            hx_target="#username_validation",
            aria_invalid="true" if error else "",
        ),
        Small(
            error,
            id="username_validation",
            _="on htmx:afterSwap add @aria-invalid='true' to #username if I am not empty",
        ),
        Input(
            type="password",
            value=user.password,
            placeholder="password",
            name="password",
        ),
        Small("it's not possible to reset passwords. make sure not to loose it"),
        Button("Create account", hx_post="/signup", hx_target="form"),
        method="post",
    )


@app.post("/signup/validate")
def validate_username(name: str):
    if db.t.users.count_where("name=?", [name]) > 0:
        return "Username is already taken"


User = db.t.users.dataclass()


@app.post("/signup")
def signup(newUser: UserForm, sess):
    error = validate_username(newUser.name)
    if error is not None:
        return signup_form(newUser, error)

    user = User(name=newUser.name, password_salt=hash_password(newUser.password))
    db.t.users.insert(user)
    login(Credentials(user.name, newUser.password), sess)
    return Response(headers={"HX-Location": "/"})


def create_car_form():
    return
