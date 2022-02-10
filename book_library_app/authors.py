from flask import jsonify,request
from book_library_app import app
from book_library_app.models import Author , AuthorSchema, author_schema


@app.route('/api/v1/authors', methods=['GET'])
def get_authors():
    authors=Author.query.all()
    author_schema=AuthorSchema(many=True)

    return jsonify({
        'success': True,
        'data': author_schema.dump(authors),
        'numbers_of_records': len(authors)
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['GET'])
def get_author(author_id: int):
    authors=Author.query.get_or_404(author_id,description=f'Author with id: {author_id} not found')
    
    return jsonify({
        'success': True,
        'data': author_schema.dump(authors)
    })


@app.route('/api/v1/authors', methods=['POST'])
def create_author():
    data=request.get_json()
    first_name=data.get('first_name')
    last_name=data.get('last_name')
    birth_date=data.get('birth_date')
    author=Author(first_name=first_name,last_name=last_name,birth_date=birth_date)
    print(author)
    return jsonify({
        'success': True,
        'data': 'New author has been created'
    }), 201


@app.route('/api/v1/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id: int):
    return jsonify({
        'success': True,
        'data': f'Author with id: {author_id} has been updated'
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id: int):
    return jsonify({
        'success': True,
        'data': f'Author with {author_id} has been deleted'
    })
