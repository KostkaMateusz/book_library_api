from flask import jsonify, abort
from webargs.flaskparser import use_args
from book_library_app import db
from book_library_app.models import Votes, VotesSchema, votes_schema
from book_library_app.votes import votes_bp
from book_library_app.utils import (
    get_schema_args,
    apply_order,
    apply_filter,
    get_pagination,
    token_required,
    calculate_stats,
    validate_json_content_type,
)


@votes_bp.route("/votes", methods=["GET"])
def get_votes():
    """Querry table Votes and returns data as json"""
    query = Votes.query
    query = apply_order(Votes, query)
    query = apply_filter(Votes, query)
    items, pagination = get_pagination(query, "votes.get_votes")

    schema_args = get_schema_args(Votes)
    books = VotesSchema(**schema_args).dump(items)

    return jsonify(
        {
            "data": books,
            "numbers_of_records": len(books),
            "pagination": pagination,
        }
    )


@votes_bp.route("/vote/<int:book_id>", methods=["GET"])
def get_vote(book_id):

    votes_list = Votes.query.filter(Votes.book_id == book_id).all()

    return jsonify({"data": votes_schema.dump(votes_list, many=True)})


@votes_bp.route("/vote", methods=["POST"])
@token_required
@validate_json_content_type
@use_args(VotesSchema, error_status_code=400)
def create_vote(user_id: int, args: dict):

    vote = Votes(user_id=user_id, **args)

    if Votes.query.filter(
        Votes.user_id == user_id, Votes.book_id == args["book_id"]
    ).first():
        abort(409, description=("User already add comment on this book"))

    db.session.add(vote)
    db.session.commit()
    calculate_stats([vote.book_id])

    return (
        jsonify(
            {
                "data": votes_schema.dump(vote),
            }
        ),
        201,
    )


@votes_bp.route("/vote/<int:comment_id>", methods=["PUT"])
@token_required
@validate_json_content_type
@use_args(VotesSchema, error_status_code=400)
def edit_comment(user_id: int, args: dict, comment_id: int):

    vote = Votes.query.get_or_404(
        comment_id, description=f"Comment with id: {comment_id} not found"
    )

    if user_id != vote.user_id:
        abort(409, description="This comment do not belong to this user")

    vote.points = args["points"]
    args["comment_text"]
    vote.comment_text = args["comment_text"]

    db.session.commit()
    calculate_stats([vote.book_id])

    return (
        jsonify(
            {
                "data": votes_schema.dump(vote),
            }
        ),
        201,
    )


@votes_bp.route("/vote/<int:comment_id>", methods=["DELETE"])
@token_required
@use_args(VotesSchema, error_status_code=400)
def delete_comment(user_id: int, args: dict, comment_id: int):

    vote = Votes.query.get_or_404(
        comment_id, description=f"Comment with id: {comment_id} not found"
    )

    if user_id != vote.user_id:
        abort(409, description="This comment do not belong to this user")

    db.session.delete(vote)
    db.session.commit()

    calculate_stats([vote.book_id])

    return (
        jsonify({"data": "Data has been deleted", "book_id": vote.book_id}),
        201,
    )
