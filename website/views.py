from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from werkzeug.security import generate_password_hash
import random
import string

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_created.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", user=current_user, posts=posts)


# Route trang Admin
@views.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash("Bạn không có quyền truy cập vào trang Admin!", category="error")
        return redirect(url_for("views.home"))
    
    users = User.query.all()
    return render_template("admin.html", users=users, user=current_user)

# Route khóa/mở khóa user
@views.route("/block-user/<int:user_id>")
@login_required
def block_user(user_id):
    if not current_user.is_admin:
        flash("Bạn không có quyền thực hiện thao tác này!", category="error")
        return redirect(url_for("views.admin"))

    user = User.query.get(user_id)
    if user:
        user.is_blocked = not user.is_blocked
        db.session.commit()
        flash(f"User {user.username} đã được {'bị khóa' if user.is_blocked else 'mở khóa'}.", category="success")
    
    return redirect(url_for("views.admin"))

# Route reset mật khẩu
@views.route("/reset-password/<int:user_id>")
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        flash("Bạn không có quyền thực hiện thao tác này!", category="error")
        return redirect(url_for("views.admin"))

    user = User.query.get(user_id)
    if user:
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash(f"Mật khẩu của {user.username} đã được reset thành: {new_password}", category="success")
    
    return redirect(url_for("views.admin"))
@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})