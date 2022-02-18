from flask import Blueprint



votes_bp=Blueprint('votes',__name__)


from book_library_app.votes import votes