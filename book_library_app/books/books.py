from pydoc import describe
from flask import jsonify,abort
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
    schema_args = get_schema_args(Book)
    query = apply_order(Book, query)
    query = apply_filter(Book, query)
    items, pagination = get_pagination(query, 'books.get_books')
    # here we dynamicly build arguments to a function in form of dict
    # and later we konwert dic with ** notation to key_word arguments

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
def update_book(args:dict,book_id: int):
    print("here1")
    book = Book.query.get_or_404(book_id, description=f'Book with id: {book_id} not found')
    if Book.query.filter(Book.isbn==args["isbn"]).first():
        abort(409, description=(f'Book with ISBN { args["isbn"] } alredy exists'))
    
    book.title=args['title']
    book.isbn=args['isbn']
    book.number_of_pages=args['number_of_pages']
    description=args.get('desciption')

    if description is not None:
        book.description=description
    
    author_id=args.get('author_id')
    if author_id is not None:
        Author.query.get_or_404(author_id, description=f'Author with id: {book_id} not found')
        book.author_id=author_id
    
    
    db.session.commit()

    return jsonify({
        'success': True,
        'data': book_schema.dump(book)
    })
