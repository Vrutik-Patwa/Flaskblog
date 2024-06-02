# routes.py
import secrets
import os
from flask import Flask, render_template, flash, redirect, url_for, request, abort
from Flaskblog import app, db, bcrypt
from Flaskblog.models import User, post
from Flaskblog.Forms import RegistrationForm, LoginForm, UpdateForm, PostForms
from wtforms.validators import ValidationError
from flask_login import login_user, current_user, logout_user, login_required
with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, int)
    data = post.query.paginate(page=page, per_page=5)

    return render_template('Home.html', posts=data)


@app.route("/about")
def about():
    return render_template('About.html', title='about')


@app.route('/Register', methods=['GET', 'POST'])
def Register():
    # if current_user.is_authenticatedj:
    #     return redirect(url_for('home'))
    Form = RegistrationForm()
    print(Form)
    if Form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(
            Form.password.data).decode('utf-8')
        user = User(username=Form.username.data,
                    Email=Form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created for {Form.username.data}!', 'success')

        return redirect(url_for('Login'))
    # else:
        #
    #    print(Form.validate_username(username=Form.username))
    #    print((Form.username.data))
    return render_template('Register.html', title='Register', form=Form)


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    Form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if Form.validate_on_submit():
        # print("In login")
        user = User.query.filter_by(Email=Form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, Form.password.data):
            # print("In if")
            login_user(user, remember=Form.remember.data)
            return redirect(url_for('home'))

        else:  # if Form.email.data=='admin@blog.com' and Form.password.data=='password':
            print("in else")
            flash(f'Login Unsucessful!', 'error')
        #     if()
    return render_template('Login.html', title='Login', form=Form)


@app.route('/Logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/Profile', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@app.route("/account", methods=['Get', 'Post'])
@login_required
def account():
    Form = UpdateForm()
    if Form.validate_on_submit():
        if Form.picture.data:
            print("Here")
            picture_file = save_picture(Form.picture.data)
            current_user.image_file = picture_file
        print("here in sybmit")
        current_user.username = Form.username.data
        current_user.Email = Form.email.data
        db.session.commit()
        flash(f'Account Updated for {Form.username.data}!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        Form.username.data = current_user.username
        Form.email.data = current_user.Email
    image_file = url_for('static', filename='Profile/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=Form)


@app.route("/posts/add", methods=['GET', 'POST'])
@login_required
def new_post():
    Form = PostForms()

    if Form.validate_on_submit():
        pos = post(title=Form.title.data,
                   content=Form.content.data, author=current_user)
        db.session.add(pos)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title="New_post", form=Form, legend="New Post")


@app.route("/post/<int:post_id>")
def posts(post_id):
    pos = post.query.get_or_404(post_id)
    return render_template('post.html', title=pos.title, post=pos)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    pos = post.query.get_or_404(post_id)
    if (pos.author != current_user):
        abort(403)
    form = PostForms()
    if form.validate_on_submit():
        pos.title = form.title.data
        pos.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('posts', post_id=pos.id))
    elif request.method == 'GET':
        form.title.data = pos.title
        form.content.data = pos.content
    return render_template('update_post.html', post=pos, title="Update_Posy", form=form, legend='Update')


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    pos = post.query.get_or_404(post_id)
    if (pos.author != current_user):
        abort(403)
    db.session.delete(pos)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))
