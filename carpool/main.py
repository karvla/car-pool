from dotenv import load_dotenv
from app import serve, app, rt
from fasthtml.common import Titled, A
import bookings
import login

load_dotenv()


@rt("/")
def get():
    return Titled(
        "Car pool",
        A("New booking", href="/bookings/add"),
        bookings.bookings_table(),
    )


if __name__ == "__main__":
    serve()
