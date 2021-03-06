from sre_constants import SUCCESS
from flask import jsonify, abort
from book_library_app import db
from book_library_app.utils import validate_json_content_type
from book_library_app.models import Book, BookSchema, book_schema, Author
from webargs.flaskparser import use_args
from book_library_app.books import books_bp
from book_library_app.utils import (
    calculate_stats,
    get_schema_args,
    apply_order,
    apply_filter,
    get_pagination,
    token_required,
    get_book_cover_link,
    upload_file_s3_bucket,
)


# add defoult cover
@books_bp.route("/books", methods=["GET"])
def get_books():
    """Query table Authors and returns data as json"""
    query = Book.query
    query = apply_order(Book, query)
    query = apply_filter(Book, query)
    items, pagination = get_pagination(query, "books.get_books")

    # specify what fields are to be serialized Schema(only=[fields])
    schema_args = get_schema_args(Book)

    books = BookSchema(**schema_args).dump(items)

    if "only" in schema_args.keys() and "cover_name" in schema_args["only"]:
        for book in books:
            book["cover_name"] = get_book_cover_link(book["cover_name"])

    return jsonify(
        {
            "data": books,
            "numbers_of_records": len(books),
            "pagination": pagination,
        }
    )


@books_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int):

    book = Book.query.get_or_404(
        book_id, description=f"Book with id: {book_id} not found"
    )

    calculate_stats([book_id])
    book_json = book_schema.dump(book)
    book_json["cover_name"] = get_book_cover_link(book_json["cover_name"])

    return jsonify(
        {
            "data": book_json,
        }
    )


@books_bp.route("/books/<int:book_id>", methods=["PUT"])
@token_required
@validate_json_content_type
@use_args(book_schema, error_status_code=400)
def update_book(author_id: str, args: dict, book_id: int):
    book = Book.query.get_or_404(
        book_id, description=f"Book with id: {book_id} not found"
    )
    if Book.query.filter(Book.isbn == args["isbn"]).first():
        abort(409, description=(f'Book with ISBN { args["isbn"] } alredy exists'))

    book.title = args["title"]
    book.isbn = args["isbn"]
    book.number_of_pages = args["number_of_pages"]
    description = args.get("desciption")

    if description is not None:
        book.description = description

    author_id = args.get("author_id")
    if author_id is not None:
        Author.query.get_or_404(
            author_id, description=f"Author with id: {book_id} not found"
        )
        book.author_id = author_id

    db.session.commit()

    return jsonify({"data": book_schema.dump(book)})


@books_bp.route("/book/<int:book_id>/cover", methods=["POST"])
@token_required
def update_cover(user_id, book_id):
    book = Book.query.get_or_404(
        book_id, description=(f"Book with id: {book_id} not found")
    )
    cover_name_with_id = "cover" + str(book.id)
    cover_name_with_extension = upload_file_s3_bucket(cover_name_with_id)

    if cover_name_with_extension is not None:
        book.cover_name = cover_name_with_extension
        db.session.commit()

    return jsonify({"success": "True"})


@books_bp.route("/books/<int:book_id>", methods=["DELETE"])
@token_required
def delete_book(author_id: str, book_id: int):
    book = Book.query.get_or_404(
        book_id, description=f"Author with id: {book_id} not found"
    )

    db.session.delete(book)
    db.session.commit()

    return jsonify({"data": f"Book with {book_id} has been deleted"})


@books_bp.route("/authors/<int:author_id>/books", methods=["GET"])
def get_all_author_books(author_id: int):
    Author.query.get_or_404(author_id, description=f"Author with {author_id} not found")
    books = Book.query.filter(Book.author_id == author_id).all()

    items = BookSchema(many=True, exclude=["author"]).dump(books)

    return jsonify({"data": items, "number_of_records": len(items)})


@books_bp.route("/authors/<int:author_id>/books", methods=["POST"])
@token_required
@validate_json_content_type
@use_args(BookSchema(exclude=["author_id"]), error_status_code=400)
def create_book(user_id: int, args: dict, author_id: str):
    Author.query.get_or_404(author_id, description=f"Author with {author_id} not found")
    if Book.query.filter(Book.isbn == args["isbn"]).first():
        abort(409, description=(f'Book with ISBN { args["isbn"] } already exists'))

    book = Book(author_id=author_id, **args)
    db.session.add(book)
    db.session.commit()

    return jsonify(
        {
            "data": book_schema.dump(book),
        }
    )
