from hardwarecheckout import app

import os

from hardwarecheckout.utils import requires_auth, requires_admin
from hardwarecheckout.models.user import User
from hardwarecheckout.models.request import Request, RequestStatus
from hardwarecheckout.models import db

from hardwarecheckout.forms.user_update_form import UserUpdateForm

from werkzeug.utils import secure_filename

from flask import (
    jsonify,
    send_from_directory,
    request,
    redirect,
    render_template,
)

UPLOAD_FOLDER = "cv"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# limit max upload size to 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']

def allowed_filename(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user')
@requires_auth()
def get_user():
    # render user page, with options to change settings etc
    return render_template('pages/user.html',
            requests = Request.query.filter_by(user_id = user.id).order_by(Request.timestamp.desc()).all(),
            user = user,
            isme = True,
            target = user,
            RequestStatus = RequestStatus)

@app.route('/user/<int:id>')
@requires_auth()
def user_items(id):
    # display items signed out by user
    # only works for user if they match id, works for admins
    is_me = (user.id == id)
    target = User.query.get(id)
    return render_template('pages/user.html',
            requests = Request.query.filter_by(user_id = target.id).order_by(Request.timestamp.desc()).all(),
            user = user,
            target = target,
            RequestStatus = RequestStatus,
            isme = is_me,
            items = target.items)

@app.route('/cvupload', methods=['POST'])
@requires_auth()
def cvupload():
    if 'cv' not in request.files:
        return jsonify(
            success=False,
            reason="No file part"
        )

    file_ = request.files['cv']

    if file_.filename == '':
        return jsonify(
            success=False,
            reason="No file provided"
        )

    if file_ and allowed_filename(file_.filename):
        filename = secure_filename(str(user.id) + file_.filename)
        file_.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify(
            success=True
        )
    return jsonify(
        success=False,
        reason="Function fell out"
    )

@app.route('/user/<int:id>/update', methods=['POST'])
@requires_auth()
def user_update(id):
    # update user settings
    if user.is_admin or user.id == id:
        user_to_change = User.query.get(id)
        form = UserUpdateForm(request.form)
        if form.validate(): 
            if form.location.data:
                user_to_change.location = form.location.data
            if form.phone.data:
                user_to_change.phone = form.phone.data.national_number
            if form.name.data:  
                user_to_change.name = form.name.data
            db.session.commit()
            return jsonify(
                success=True
            ) 

        error_msg = '\n'.join([key.title() + ': ' + ', '.join(value) for key, value in form.errors.items()])

        return jsonify(
            success=False,
            message=error_msg,
            user={
                'phone': user_to_change.phone,
                'name': user_to_change.name,
                'location': user_to_change.location
            }
        )

    else:
        return jsonify(
            success=False,
            message='Forbidden'
        ), 403

@app.route('/users')
@requires_admin()
def get_users():
    # render list of all users 
    return render_template('pages/users.html',
            user = user,
            users = User.query.all())
