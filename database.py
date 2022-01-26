from server import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

# CONFIGURE TABLE
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=100)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    posts = relationship("BlogPost", back_populates="author")

# Run only once for creating a database
# db.create_all()

# Read all blog posts
def read_all():
    all_posts = db.session.query(BlogPost).all()
    return all_posts

# Add blog post
def add_post(title, subtitle, date, body, author, img_url):
    user_id = User.query.filter_by(name=author).first()
    post = BlogPost(
        title=title,
        subtitle=subtitle,
        date=date,
        body=body,
        author_id=user_id,
        img_url=img_url
    )
    db.session.add(post)
    db.session.commit()

# Read blog post
def read_post_by_id(post_id):
    post = BlogPost.query.filter_by(id=post_id).first()
    return post

# Update blog post data
def update_post(post_id, title, subtitle, body, author, img_url):
    user_id = User.query.filter_by(name=author).first()
    post = BlogPost.query.filter_by(id=post_id).first()
    post.title = title
    post.subtitle = subtitle
    post.body = body
    post.author = user_id
    post.img_url = img_url
    db.session.commit()

# Delete post by id
def delete_post_from_db(post_id):
    post_del = BlogPost.query.get(post_id)
    db.session.delete(post_del)
    db.session.commit()

# Add user to db
def add_new_user(user_email, user_password, username):
    user = User(
        email=user_email,
        password=user_password,
        name=username
    )
    db.session.add(user)
    db.session.commit()

    return user