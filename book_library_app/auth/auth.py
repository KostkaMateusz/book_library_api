from book_library_app.auth import auth_bp
from book_library_app.utils import token_required, validate_json_content_type, email_sender
from webargs.flaskparser import use_args
from book_library_app.models import HashResetTable, UserSchema, user_schema, User, user_password_update_schema, UserPasswordUpdateSchema
from flask import jsonify, abort, url_for
from book_library_app import db


@auth_bp.route('/register', methods=['POST'])
@validate_json_content_type
@use_args(user_schema, error_status_code=400)
def register(args: dict):
    if User.query.filter(User.username == args["username"]).first():
        abort(409, description=(
            f'User with username { args["username"] } alredy exists'))

    if User.query.filter(User.email == args["email"]).first():
        abort(409, description=(
            f'User with email { args["email"] } alredy exists'))

    args['password'] = User.generate_hashed_password(args['password'])
    user = User(**args)

    db.session.add(user)
    db.session.commit()

    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    }), 201


@auth_bp.route('/login', methods=['POST'])
@validate_json_content_type
@use_args(UserSchema(only=['username', 'password']), error_status_code=400)
def login(args: dict):
    user = User.query.filter(User.username == args["username"]).first()
    if not user:
        abort(401, description=('Invalid credentials'))

    if not user.is_password_valid(args['password']):
        abort(401, description=('Invalid credentials'))

    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    })


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(user_id: int):
    user = User.query.get_or_404(
        user_id, description=f'User with id {user_id} not found')

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })


@auth_bp.route('/update/password', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(user_password_update_schema, error_status_code=400)
def update_user_password(user_id: int, args):
    user = User.query.get_or_404(
        user_id, description=f'User with id {user_id} not found')

    if not user.is_password_valid(args['current_password']):
        abort(401, description='Invalid password')

    user.password = user.generate_hashed_password(args['new_password'])
    db.session.commit()
    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })


@auth_bp.route('/update/data', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(UserSchema(only=['username', 'email']), error_status_code=400)
def update_user_data(user_id: int, args):

    if User.query.filter(User.username == args["username"]).first():
        abort(409, description=(
            f'User with username { args["username"] } alredy exists'))

    if User.query.filter(User.email == args["email"]).first():
        abort(409, description=(
            f'User with email { args["email"] } alredy exists'))

    user = User.query.get_or_404(
        user_id, description=f'User with id {user_id} not found')

    user.username = args['username']
    user.email = args['email']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })


@auth_bp.route('/reset/<string:hash>', methods=['PUT'])
@validate_json_content_type
@use_args(UserPasswordUpdateSchema(only=['new_password']), error_status_code=400)
def reset_password(args: dict, hash: str):

    hash_record = HashResetTable.query.filter(
        HashResetTable.hash_code == hash).first()
    if hash_record is None:
        abort(404, "Invalid adres site")

    user = User.query.get_or_404(
        hash_record.user_id, description=f'Wrong adres')

    if user.is_password_valid(args['new_password']):
        db.session.delete(hash_record)
        abort(401, "New password can't be the same as old one")

    user.password = User.generate_hashed_password(args['new_password'])

    db.session.delete(hash_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Password for user: {user.username} has been change'
    })


@auth_bp.route('/reset/password', methods=['POST'])
@validate_json_content_type
@use_args(UserSchema(only=['email']), error_status_code=400)
def send_recovery_email(args: dict):
    text = ""
    user = User.query.filter(User.email == args['email']).first()
    if user is None:
        text = """\
            Somebody ask for reset password with this email.
            If this was not you please ignore this message. 
            If this was you try register then.
            Best regards :D 
            """
        email_sender(args['email'], text)
    else:

        hash = HashResetTable()
        hash.hash_code = hash.generate_jwt()
        hash.user_id = user.id
        db.session.add(hash)
        db.session.commit()

        text = f"""\
            Your reset password link:
            {url_for('auth.reset_password',**{"hash":hash.hash_code})}
            
            Best regards :D 
            """

        email_sender(args['email'], text, hashCode=hash.hash_code)

    return jsonify({
        'success': True,
        'data': 'Reset link has been send to provided email'
    })
