import ssl
import smtplib
import os
import re
import jwt
from functools import wraps
from typing import Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import request, url_for, current_app, abort
from flask_sqlalchemy import DefaultMeta, BaseQuery
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from book_library_app.models import Author, Votes, Book
from book_library_app import db
from werkzeug.exceptions import UnsupportedMediaType

COMPARISION_OPERATORS_RE = re.compile(r"(.*)\[(gte|gt|lte|lt)\]")


def calculate_stats(books_id: list[int]) -> None:
    """Calculate book score and number of votes based on book id and data in Votes table"""
    for book_id in books_id:
        votes_list = Votes.query.filter(Votes.book_id == book_id).all()
        book = Book.query.get_or_404(
            book_id, description=f"Book with id: {book_id} not found"
        )
        book.score_sum = sum([vote.points for vote in votes_list])
        book.number_of_votes = len(votes_list)
        if book.number_of_votes != 0:
            book.average_book_score = book.score_sum / book.number_of_votes
        else:
            book.average_book_score = 0

        db.session.commit()
        calculate_authors_stats(author_id=book.author_id)


def calculate_authors_stats(author_id: int, db_save=True) -> None:
    """Calculate author score if db_save is set to false db save is turned off"""
    author = Author.query.get_or_404(
        author_id, description=f"Author with id: {author_id} not found"
    )
    books = Book.query.filter(Book.author_id == author_id).all()
    print(f"books:{books}")
    sum_average_scores_book = 0
    for book in books:
        if book.average_book_score is not None:
            sum_average_scores_book += book.average_book_score
    number_of_author_books = len(books)
    author.author_average_score = (
        sum_average_scores_book / number_of_author_books
        if number_of_author_books != 0
        else 0
    )
    if db_save is True:
        db.session.commit()


def validate_json_content_type(func):
    """Custom decorator check if send data from request is in json data format"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None:
            raise UnsupportedMediaType("Content type must be appliacation/json")
        return func(*args, **kwargs)

    return wrapper


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        auth = request.headers.get("Authorization")
        if auth:
            token = auth.split(" ")[1]
        if token is None:
            abort(404, description="Missing token. Please login or register")

        try:
            payload = jwt.decode(
                token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            abort(404, description="Token expired. Please login to get new token")
        except jwt.InvalidTokenError:
            abort(404, description="Invalid token. Please login or register")
        else:
            return func(payload["user_id"], *args, **kwargs)

    return wrapper


def get_schema_args(model: DefaultMeta) -> dict:
    """Which fields are to be displayed"""
    schema_args = {"many": True}
    fields = request.args.get("fields")

    # here we dynamicly build arguments to a only parameter in Schema object in form of dict
    if fields is not None:
        schema_args["only"] = [
            field for field in fields.split(",") if field in model.__table__.columns
        ]

    return schema_args


def apply_order(model: DefaultMeta, querry: BaseQuery) -> BaseQuery:
    """Get sort arguments from request"""
    sort_keys = request.args.get("sort")
    if sort_keys is not None:
        for key in sort_keys.split(","):
            desc = False
            if key.startswith("-"):
                key = key[1:]
                desc = True
            column_attr = getattr(model, key, None)
            if column_attr is not None:
                # specify sort based of what column if desc True sort in desc order
                querry = (
                    querry.order_by(column_attr.desc())
                    if desc
                    else querry.order_by(column_attr)
                )
    return querry


def get_filter_argument(
    column_name: InstrumentedAttribute, value: str, operator: str
) -> BinaryExpression:
    """Change http arguments to a boolean expresion"""
    operator_mapping = {
        "==": column_name == value,
        "gte": column_name >= value,
        "gt": column_name > value,
        "lte": column_name <= value,
        "lt": column_name < value,
    }
    return operator_mapping[operator]


def apply_filter(model: DefaultMeta, query: BaseQuery) -> BaseQuery:
    """Show entry which meet requirments from request"""
    for param, value in request.args.items():

        # all parameters that are not in fields, sort,page and limit are filtering arguments
        if param not in {"fields", "sort", "page", "limit"}:
            # defoult operator if none argument passed
            operator = "=="
            # return what symbols patch pre-compiled pattern
            match = COMPARISION_OPERATORS_RE.match(param)
            if match is not None:
                # param-what is not matched, operator-what is matched e.g birth_date: gte
                param, operator = match.groups()
            column_attr = getattr(model, param, None)

            if column_attr is not None:
                # all data object must have implemented addidional validation function
                value = model.additional_validation(param, value)
                if value is None:
                    continue
                filter_argument = get_filter_argument(column_attr, value, operator)
                query = query.filter(filter_argument)
    return query


def get_pagination(querry: BaseQuery, func_name: str) -> Tuple:
    """Return divided data to pages with adres for next and previous page"""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", current_app.config.get("PER_PAGE", 5), type=int)
    # paginate pages save their origin parameters to a variabla and built page with them
    params = {key: value for key, value in request.args.items() if key != "page"}

    paginate_object = querry.paginate(page, limit, False)
    pagination = {
        "total_pages": paginate_object.pages,
        "total_records": paginate_object.total,
        "current_page": url_for(func_name, page=page, **params),
    }
    if paginate_object.has_next:
        pagination["next_page"] = url_for(func_name, page=page + 1, **params)

    if paginate_object.has_prev:
        pagination["previous_page"] = url_for(func_name, page=page - 1, **params)

    return paginate_object.items, pagination


def email_sender(receiver_email: str, text: str, hashCode="") -> None:

    port = 465
    email_password = os.environ.get("email_password")
    sender_email = os.environ.get("sender_email")

    contex = ssl.create_default_context()

    # Create a multipart message and set headers
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset password request"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message

    html = f"""\
    <html><body>
        <p>Hi, Book Library API HERE<br>{text}<br></p>
    </body></html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP_SSL("smtp.gmail.com", port=port, context=contex) as server:
        server.login("pocztatestowy@gmail.com", password=email_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
