from distutils.log import debug
from flask import jsonify, abort
from book_library_app import db
from book_library_app.utils import validate_json_content_type
from book_library_app.models import Book, BookSchema, book_schema, Author, Votes, VotesSchema, votes_schema
from webargs.flaskparser import use_args
from book_library_app.books import books_bp
from book_library_app.votes import votes_bp
from book_library_app.utils import get_schema_args, apply_order, apply_filter, get_pagination, token_required, calculate_stats
from book_library_app.debug import debug


@debug
@votes_bp.route('/votes', methods=['GET'])
def get_votes():
    """Querry table Votes and returns data as json"""
    query = Votes.query
    query = apply_order(Votes, query)
    query = apply_filter(Votes, query)
    items, pagination = get_pagination(query, 'votes.get_votes')

    schema_args = get_schema_args(Votes)
    books = VotesSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': books,
        'numbers_of_records': len(books), 'pagination': pagination
    })


@votes_bp.route('/vote/<int:book_id>', methods=['GET'])
def get_vote(book_id):

    votes_list = Votes.query.filter(Votes.book_id == book_id).all()

    return jsonify({
        'success': True,
        'data': votes_schema.dump(votes_list, many=True)

    })



@votes_bp.route('/vote', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(VotesSchema, error_status_code=400)
def create_vote(user_id ,args: dict):

    vote = Votes(user_id=user_id, **args)
    db.session.add(vote)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': votes_schema.dump(vote),

    }), 201
