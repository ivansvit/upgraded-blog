from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from feedback import FeedbackMessage
from flask_ckeditor import CKEditor
import database
from newblogform import CreatePostForm
from datetime import datetime
import os

feedback = FeedbackMessage()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
Bootstrap(app)
ckeditor = CKEditor(app)
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    return render_template("make-post.html", form=form)

# Edit post page
@app.route("/edit-post/<post_id>", methods=["GET", "POST"])
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

    return render_template("make-post.html", form=edit_form, is_edit=True)

# Delete post route
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    database.delete_post_from_db(post_id)
    return redirect(url_for("home_page"))



if __name__ == "__main__":
    app.run(debug=True)