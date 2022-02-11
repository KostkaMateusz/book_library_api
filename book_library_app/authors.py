from flask import jsonify, request
from book_library_app import app, db
from book_library_app.utils import validate_json_content_type
from book_library_app.models import Author, AuthorSchema, author_schema
from webargs.flaskparser import use_args


@app.route('/api/v1/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    author_schema = AuthorSchema(many=True)

    return jsonify({
        'success': True,
        'data': author_schema.dump(authors),
        'numbers_of_records': len(authors)
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['GET'])
def get_author(author_id: int):
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
    author = Author(**kwargs)
    db.session.add(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': author_schema.dump(author)
    }), 201


@app.route('/api/v1/authors/<int:author_id>', methods=['PUT'])
@validate_json_content_type
@use_args(author_schema,error_status_code=400)
def update_author(kwargs:dict , author_id: int):
    authors = Author.query.get_or_404(
        author_id, description=f'Author with id: {author_id} not found')
    authors.first_name=kwargs['first_name']
    authors.last_name=kwargs['last_name']
    authors.birth_date=kwargs['birth_date']
    
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
