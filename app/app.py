from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user
from flask_login import login_required, logout_user, current_user
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import gridfs
import pymongo
import os
import re
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max-limit

mongo_uri = os.getenv('MONGO_URI')
print(mongo_uri)
client = MongoClient(mongo_uri)

db = client.pet_base
fs = gridfs.GridFS(db)
users_collection = db.users
posts_collection = db.posts
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    """
    Represents a user in the application.

    Attributes:
        id (str): Unique identifier of the user.
        username (str): Username of the user.
    """
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        

@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the database by their user ID.

    Args:
        user_id (str): The user's ID.

    Returns:
        User: A User object if the user is found, otherwise None.
    """
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_id=user_data["_id"], username=user_data["username"])
    return None


@app.route("/home")
@login_required
def home():
    raw_posts = posts_collection.find().sort("created_at", DESCENDING)
    all_posts = []
    for post in raw_posts:
        image = fs.get(post["image_id"])
        image_url = f"/image/{post['image_id']}"
        
        all_posts.append({
            "post_id": str(post["_id"]),
            "title": post["title"],
            "image_url": image_url,
            "author": post.get("user")
        })
    return render_template("home.html", posts = all_posts)

@app.route("/followed_circle")
@login_required
def followed_circle():
    cur_user = users_collection.find_one({"username": current_user.username})
    followed_users = cur_user.get("following", [])
    raw_followed_posts = posts_collection.find({"user": {"$in": followed_users}}).sort("created_at", DESCENDING)
    followed_posts = []
    for post in raw_followed_posts:
        image = fs.get(post["image_id"])
        image_url = f"/image/{post['image_id']}"
        
        followed_posts.append({
            "post_id": str(post["_id"]),
            "title": post["title"],
            "image_url": image_url,
            "author": post.get("user")
        })
    return render_template("followed_circle.html", posts = followed_posts)

@app.route("/addpost", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        image = request.files["image"]
        
        cur_user = current_user.username
        image_id = fs.put(image.read(), filename=image.filename, content_type=image.content_type)
        cur_user_collection = db[cur_user]
        post = {
            "user": cur_user,
            "title": title,
            "content": content,
            "image_id": image_id,
            "views": 0,
            "likes": 0,
            "liked_by": [],
            "comments": [],  
            "created_at": datetime.utcnow()
        }
        inserted_post = posts_collection.insert_one(post)

        cur_user_collection.insert_one({"post_id": inserted_post.inserted_id})

        return redirect(url_for("home"))
    
    return render_template("addpost.html")



@app.route("/myInfo", methods=["GET"])
@login_required
def display_my_info():
    cur_user = current_user.username
    cur_user_collection = db[cur_user]
    
    post_refs = cur_user_collection.find()
    all_posts = []

    for post_ref in post_refs:
        post = posts_collection.find_one({"_id": post_ref["post_id"]})
        image = fs.get(post["image_id"])
        image_url = f"/image/{post['image_id']}"
        
        all_posts.append({
            "post_id": str(post["_id"]),
            "title": post["title"],
	    "image_url": image_url,
            "created_at": post.get("created_at")
        })

    return render_template("myInfo.html", posts=all_posts, username=cur_user)


@app.route("/image/<image_id>")
def get_image(image_id):
    image = fs.get(ObjectId(image_id))
    return app.response_class(image.read(), mimetype=image.content_type)


@app.route("/posts/<post_id>", methods=["GET"])
@login_required
def display_post(post_id):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    image = fs.get(post["image_id"])
    image_url = f"/image/{post['image_id']}"
    
    posts_collection.update_one(
        {"_id": ObjectId(post_id)}, 
        {"$inc": {"views": 1}}  # increment the views by 1
    )

    # Get all comments
    comments = post.get("comments", [])
    
    cur_user = current_user.username
    if cur_user in post.get('liked_by', []):
        liked = 1
    else:
        liked = 0
        
    return render_template("post.html", post=post, image_url=image_url, liked=liked)



@app.route('/like_post/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    cur_user = current_user.username

    post = posts_collection.find_one({"_id": ObjectId(post_id)})

    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if cur_user in post.get('liked_by', []):
        # User has liked the post, so remove the like
        new_like_count = post.get('likes', 0) - 1
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$pull": {"liked_by": cur_user},  # removes the user from the liked_by list
                "$set": {"likes": new_like_count}
            }
        )
        action = 'removed'
    else:
        # User has not liked the post, so add the like
        new_like_count = post.get('likes', 0) + 1
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"liked_by": cur_user},  # adds the user to the liked_by list
                "$set": {"likes": new_like_count}
            }
        )
        action = 'added'

    return jsonify({'likes': new_like_count, 'action': action})



@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration.

    If the request method is POST, processes the registration form and creates a new user.

    Returns:
        flask.Response: The rendered 'register.html' template or a redirect to the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for("register"))

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password1, method="pbkdf2:sha256")
        users_collection.insert_one({"username": username, "password": hashed_password})
        db.create_collection(username)
        # flash("Registration successful! You can now log in.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.

    If the request method is POST, processes the login form and authenticates the user.

    Returns:
        flask.Response: The rendered 'login.html' template or a redirect to the home page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_data = users_collection.find_one({"username": username})

        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_id=str(user_data["_id"]), username=user_data["username"])
            login_user(user)
            # flash("Login successful!")
            return redirect(url_for("home"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Logs out the current user and redirects to the login page.

    Returns:
        flask.Response: A redirect to the login page.
    """
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
def ini():
    """
    Redirects the root URL to the login page.

    Returns:
        flask.Response: A redirect to the login page.
    """
    return redirect(url_for("home"))

@app.route("/profile/<username>", methods=["GET"])
@login_required
def user_profile(username):
    user = users_collection.find_one({"username": username})
    if not user:
        flash("User not found.")
        return redirect(url_for("home"))

    user_posts = posts_collection.find({"user": username})
    all_posts = []

    for post in user_posts:
        image_url = f"/image/{post['image_id']}"
        all_posts.append({
            "post_id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "image_url": image_url,
            "created_at": post.get("created_at"),
        })

    is_following = current_user.username in user.get("followers", [])
    return render_template("profile.html", posts=all_posts, username=username, is_following=is_following)

@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow_user(username):
    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    cur_user = current_user.username

    if cur_user in user.get("followers", []):
        users_collection.update_one({"username": username}, {"$pull": {"followers": cur_user}})
        users_collection.update_one({"username": cur_user}, {"$pull": {"following": username}})
        action = "unfollowed"
    else:
        users_collection.update_one({"username": username}, {"$addToSet": {"followers": cur_user}})
        users_collection.update_one({"username": cur_user}, {"$addToSet": {"following": username}})
        action = "followed"
    

    updated_user = users_collection.find_one({"username": username})
    followers_count = len(updated_user.get("followers", []))

    return jsonify({"action": action, "followers_count": followers_count})


@app.route("/posts/<post_id>/comments", methods=["POST"])
@login_required
def add_comment(post_id):
    content = request.form.get("content")
    if not content.strip():
        flash("Comment cannot be empty.")
        return redirect(url_for("display_post", post_id=post_id))

    comment = {
        "username": current_user.username,
        "content": content,
        "created_at": datetime.utcnow()
    }

    posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )

    flash("Comment added successfully!")
    return redirect(url_for("display_post", post_id=post_id))


@app.route("/edit-username", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("new_username", "").strip()

        if not new_username or len(new_username) < 3:
            flash("Username must be at least 3 characters long.")
            return redirect(url_for("edit_profile"))

        existing_user = users_collection.find_one({"username": new_username})
        if existing_user:
            flash("Username already taken. Please choose a different one.")
            return redirect(url_for("edit_profile"))

        try:
            user_id = ObjectId(current_user.id)
            old_username = current_user.username
            users_collection.update_one({"_id": user_id}, {"$set": {"username": new_username}})
            db.posts.update_many({"user": old_username}, {"$set": {"user": new_username}})
            if old_username in db.list_collection_names():
                db[old_username].rename(new_username)

            current_user.username = new_username

            flash("Your username has been updated successfully!")
            return redirect(url_for("display_my_info"))
        except Exception as e:
            flash(f"An error occurred while updating your username: {e}")
            return redirect(url_for("edit_profile"))

    return render_template("edit_username.html", username=current_user.username)

@app.route("/chat")
@login_required
def chat():
    """
    Render the chat page with list of users to chat with.
    """
    # Get all users except the current user
    all_users = users_collection.find({"username": {"$ne": current_user.username}})
    users_list = [user["username"] for user in all_users]
    return render_template("chat.html", users=users_list)

@app.route("/chat/<username>", methods=["GET"])
@login_required
def chat_with_user(username):
    """
    Render chat page with a specific user
    """
    # Check if the user exists
    target_user = users_collection.find_one({"username": username})
    if not target_user:
        flash("User not found")
        return redirect(url_for("chat"))

    # Retrieve previous messages between current user and target user
    messages_collection = db.messages
    messages = messages_collection.find({
        "$or": [
            {"sender": current_user.username, "receiver": username},
            {"sender": username, "receiver": current_user.username}
        ]
    }).sort("timestamp", 1)  # Sort messages chronologically

    return render_template("chat_window.html", 
                           target_username=username, 
                           messages=list(messages),
                           current_username=current_user.username)

@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    """
    Handle sending a message
    """
    sender = current_user.username
    receiver = request.form.get("receiver")
    message = request.form.get("message")

    if not message or not receiver:
        return jsonify({"error": "Invalid message or receiver"}), 400

    messages_collection = db.messages
    message_doc = {
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": datetime.utcnow()
    }

    messages_collection.insert_one(message_doc)
    return jsonify({"status": "success"})


@app.route("/get_messages/<username>", methods=["GET"])
@login_required
def get_messages(username):
    """
    Retrieve messages between current user and specified user
    """
    messages_collection = db.messages
    messages = messages_collection.find({
        "$or": [
            {"sender": current_user.username, "receiver": username},
            {"sender": username, "receiver": current_user.username}
        ]
    }).sort("timestamp", 1)

    message_list = []
    for msg in messages:
        message_list.append({
            "sender": msg["sender"],
            "message": msg["message"],
            "timestamp": msg["timestamp"].isoformat()
        })

    return jsonify(message_list)

if __name__ == "__main__":
    # add_recommendations()
    app.run(host="0.0.0.0", port=5002, debug=True)
