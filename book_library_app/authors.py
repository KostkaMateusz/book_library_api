from flask import jsonify, request
from book_library_app import app, db
from book_library_app.utils import validate_json_content_type
from book_library_app.models import Author, AuthorSchema, author_schema
from webargs.flaskparser import use_args

# request handling functions


@app.route('/api/v1/authors', methods=['GET'])
def get_authors():
    """Querry table Authors and returns data as json"""
    query = Author.query
    query = Author.apply_order(query)
    query = Author.apply_filter(query)
    items,pagination=Author.get_pagination(query)
    # here we dynamicly build arguments to a function in form of dict
    # and later we konwert dic with ** notation to key_word arguments
    schema_args = Author.get_schema_args(request.args.get('fields'))
    
    authors = AuthorSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': authors,
        'numbers_of_records': len(authors),
        'pagination':pagination
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['GET'])
def get_author(author_id: int):
    """Querry DB in for a specyfic id if not found returns 404 error 
which is handled"""
    authors = Author.query.get_or_404(
        author_id, description=f'Author with id: {author_id} not found')
    return jsonify({
        'success': True,
        'data': author_schema.dump(authors)
    })


@app.route('/api/v1/authors', methods=['POST'])
@validate_json_content_type
@use_args(author_schema, error_status_code=400)
def create_author(kwargs: dict):
    """Becouse of data input from user we first in wrapper validate correct data format.
    Then we use webargs library to validate user input based of marshmalow schema"""
    author = Author(**kwargs)
    db.session.add(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': author_schema.dump(author)
    }), 201


@app.route('/api/v1/authors/<int:author_id>', methods=['PUT'])
@validate_json_content_type
@use_args(author_schema, error_status_code=400)
def update_author(kwargs: dict, author_id: int):
    authors = Author.query.get_or_404(
        author_id, description=f'Author with id: {author_id} not found')
    # change data in object fields and then commit them
    authors.first_name = kwargs['first_name']
    authors.last_name = kwargs['last_name']
    authors.birth_date = kwargs['birth_date']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': author_schema.dump(authors)
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id: int):
    authors = Author.query.get_or_404(
        author_id, description=f'Author with id: {author_id} not found')

    db.session.delete(authors)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Author with {author_id} has been deleted'
    })
