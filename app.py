from flask import Flask, request, redirect, render_template, flash
#from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Tag, User, Post
# depicated? ==> 
#from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

# indicate that we use postgresql and database called blogly
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "SECRET!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
#debug = DebugToolbarExtension(app)

#with app.app_context() :
#    connect_db(app)

connect_db(app)
app.app_context().push()
db.create_all()

@app.route('/')
def homepage():
    return redirect("/users")

############## USERS'S ROUTES
@app.route('/users')
def list_users():
    """show list of users and hyperlink to their details to update or delete"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("users/index.html", users=users)

@app.route('/users/<int:user_id>')
def user_show(user_id):
    """show specific user's info"""
    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)

@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """show edit form"""
    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)
    
@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """handle form submission for user's update"""
    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']
    
    db.session.add(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_delete(user_id):
    """handle form submission to delete user's profile"""
    
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return redirect('/users')

@app.route('/users/new')
def add_user():
    """show form to add new user"""
    return render_template('users/new.html')

@app.route('/users/new', methods=["POST"])
def create_user():
    """handle new user form submission"""
    new_user = User(
        first_name = request.form['first_name'],
        last_name = request.form['last_name'],
        image_url = request.form['image_url'] or None)
    
    db.session.add(new_user)
    db.session.commit()
    
    return redirect('/users')

################ POST'S ROUTES
@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    """show crate new post form for user with id no = user_id"""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('posts/new.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """handle new post form submission"""
    
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    new_post = Post(title = request.form['title'],
                    content = request.form['content'], user = user, tags=tags)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title} added.")
    return redirect(f'/users/{user_id}')

@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a specific post with info."""
    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Show edit form of the existing post"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('posts/edit.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handle edit form to update the existing post"""
    
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']
    
    tag_ids = [int(num) for num in request.form.getlist("tag")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    
    db.session.add(post)
    db.session.commit()
    flash(f"Post '{{post.title}}' edited.")
    
    return redirect (f'/users/{post.user_id}')

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_delete(post_id):
    
    post = Post.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted.")
    
    return redirect(f'/users/{post.user_id}')

############################################################
## tag

@app.route('/tags')
def tag_index():
    """show all tags"""
    
    tags = Tag.query.all()
    return render_template('tags/index.html', tags = tags)

@app.route('/tags/new', methods=["GET"])
def tags_new_form():
    """form to create a tag"""
    
    posts = Post.query.all()
    return render_template('tags/new.html', posts=posts)

@app.route('/tags/new', methods=["POST"])
def tags_new():
    """handle form submission for creating a new tag"""
    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form["name"], posts=posts)
    
    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag 'new_tag.name' added.")
    
    return redirect('/tags')
    
@app.route('/tags/<int:tag_id>')
def tag_show(tag_id):
    """show detail about a tag."""
   
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit')
def tag_edit_form(tag_id):
    """show a form to edit an existing tag"""
   
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    
    return render_template('/tags/edit.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tag_edit(tag_id):
    """handel form submission for updating an existing tag"""
    
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form["name"]
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()
    
    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' added.")
    
    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tag_delete(tag_id):
    """handle form submission for deleting an existing tag"""
    
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")
    
    return redirect("/tags")
    