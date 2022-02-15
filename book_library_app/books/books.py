from flask import jsonify, abort
from book_library_app import db
from book_library_app.utils import validate_json_content_type
from book_library_app.models import Book, BookSchema, book_schema, Author
from webargs.flaskparser import use_args
from book_library_app.books import books_bp
from book_library_app.utils import get_schema_args, apply_order, apply_filter, get_pagination


@books_bp.route('/books', methods=['GET'])
def get_books():
    """Querry table Authors and returns data as json"""
    query = Book.query
    query = apply_order(Book, query)
    query = apply_filter(Book, query)
    items, pagination = get_pagination(query, 'books.get_books')

    # specify what fields are to be serialized Schema(only=[fields])
    schema_args = get_schema_args(Book)
    books = BookSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': books,
        'numbers_of_records': len(books),
        'pagination': pagination
    })


@books_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id: int):
    """Querry DB in for a specyfic id if not found returns 404 error 
which is handled"""
    books = Book.query.get_or_404(
        book_id, description=f'Author with id: {book_id} not found')
    return jsonify({
        'success': True,
        'data': book_schema.dump(books)
    })


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@validate_json_content_type
@use_args(book_schema, error_status_code=400)
def update_book(args: dict, book_id: int):
    print("here1")
    book = Book.query.get_or_404(
        book_id, description=f'Book with id: {book_id} not found')
    if Book.query.filter(Book.isbn == args["isbn"]).first():
        abort(409, description=(
            f'Book with ISBN { args["isbn"] } alredy exists'))

    book.title = args['title']
    book.isbn = args['isbn']
    book.number_of_pages = args['number_of_pages']
    description = args.get('desciption')

    if description is not None:
        book.description = description

    author_id = args.get('author_id')
    if author_id is not None:
        Author.query.get_or_404(
            author_id, description=f'Author with id: {book_id} not found')
        book.author_id = author_id

    db.session.commit()

    return jsonify({
        'success': True,
        'data': book_schema.dump(book)
    })


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id: int):
    book = Book.query.get_or_404(
        book_id, description=f'Author with id: {book_id} not found')

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Book with {book_id} has been deleted'
    })


@books_bp.route('/authors/<int:author_id>/books', methods=['GET'])
def get_all_author_books(author_id: int):
    Author.query.get_or_404(
        author_id, description=f'Author with {author_id} not found')
    books = Book.query.filter(Book.author_id == author_id).all()

    items = BookSchema(many=True, exclude=['author']).dump(books)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })


@books_bp.route('/authors/<int:author_id>/books', methods=['POST'])
@validate_json_content_type
@use_args(BookSchema(exclude=['author_id']), error_status_code=400)
def create_book(args: dict, author_id: int):
    Author.query.get_or_404(
        author_id, description=f'Author with {author_id} not found')
    if Book.query.filter(Book.isbn == args["isbn"]).first():
        abort(409, description=(
            f'Book with ISBN { args["isbn"] } alredy exists'))

    book = Book(author_id=author_id, **args)
    db.session.add(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': book_schema.dump(book),

    }), 201
