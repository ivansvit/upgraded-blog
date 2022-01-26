from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from feedback import FeedbackMessage
from flask_ckeditor import CKEditor
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import database
from newblogform import CreatePostForm, CreateUserForm, LoginForm
from datetime import datetime
import os

# TODO 3. Update bacground images for each page

feedback = FeedbackMessage()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
Bootstrap(app)
ckeditor = CKEditor(app)
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login manager init
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return database.User.query.get(user_id)


# Create admin only access decorator
def admin_only(func):
    wraps(func)

    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403, "You have not access to this page")
        return func(*args, **kwargs)

    # Renaming the function name
    decorated_func.__name__ = func.__name__
    return decorated_func


# Home page
@app.route("/")
def home_page():
    blog_posts = database.read_all()
    return render_template("index.html", posts=blog_posts)


# About page
@app.route("/about")
def about():
    return render_template("about.html")


# Contact page
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "GET":
        label = "Contact Me"
        return render_template("contact.html", msg=label)
    else:
        # Receive all data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        user_message = request.form['message']
        message = f"Subject:New feedback\n\n" \
                  f"Name: {name}\n" \
                  f"Email: {email}\n" \
                  f"Phone Number: {phone}\n" \
                  f"Message: {user_message}"
        label = "Successfully sent your message!"
        # Send feedback
        feedback.receive_msg(message)
        return render_template("contact.html", msg=label)


# Post page
@app.route("/post/<id>")
def post_page(id):
    blog_posts = database.read_all()
    post = blog_posts[int(id) - 1]
    return render_template("post.html", post=post)


# New post page
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        database.add_post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=datetime.now().strftime("%B %d, %Y"),
            author=form.author.data,
            img_url=form.img_url.data,
            body=form.body.data
        )
        return redirect(url_for('home_page'))
    return render_template("make-post.html", form=form, current_user=current_user)


# Edit post page
@app.route("/edit-post/<post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = database.read_post_by_id(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        database.update_post(
            post_id=post_id,
            title=edit_form.title.data,
            subtitle=edit_form.subtitle.data,
            author=edit_form.author.data,
            body=edit_form.body.data,
            img_url=edit_form.img_url.data
        )
        return redirect(url_for("post_page", id=post_id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# Delete post route
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    database.delete_post_from_db(post_id)
    return redirect(url_for("home_page"))


# Register user page
@app.route("/register", methods=["GET", "POST"])
def register():
    user_form = CreateUserForm()
    if user_form.validate_on_submit():
        # Check if an email is already exist in the database
        user = database.User.query.filter_by(email=user_form.email.data).first()
        if not user:
            new_user = database.add_new_user(
                user_email=user_form.email.data,
                user_password=generate_password_hash(user_form.password.data, "pbkdf2:sha256", 8),
                username=user_form.name.data
            )

            # Log in and authenticate user after adding details to database.
            login_user(new_user)

            return redirect(url_for("home_page"))
        else:
            error = "You've already signed up with this email"
            flash(error)

    return render_template("register.html", form=user_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # Check if an email is already exist in the database
        user = database.User.query.filter_by(email=login_form.email.data).first()

        if user:
            if check_password_hash(user.password, login_form.password.data):
                login_user(user)
                return redirect(url_for("home_page"))
            else:
                error = "Invalid password"
                flash(error)
        else:
            error = "This user doesn't exist in the database."
            flash(error)

    return render_template("login.html", form=login_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home_page"))


if __name__ == "__main__":
    app.run(debug=True)
