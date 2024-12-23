from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# JSON file to store blog posts
DATA_FILE = 'blog_posts.json'
COMMENTS_FILE = 'comments.json'


# Load posts from the JSON file
def load_posts():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Save posts to the JSON file
def save_posts(posts):
    with open(DATA_FILE, 'w') as file:
        json.dump(posts, file, indent=4)


# Load comments from the JSON file
def load_comments():
    try:
        with open(COMMENTS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# Save comments to the JSON file
def save_comments(comments):
    with open(COMMENTS_FILE, 'w') as file:
        json.dump(comments, file, indent=4)


# Initial posts and comments loaded from the file
posts = load_posts()
comments = load_comments()


# Initialize likes for posts
def initialize_likes():
    for post in posts:
        if 'likes' not in post:
            post['likes'] = 0
    save_posts(posts)


initialize_likes()


# Homepage: List all blog posts
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_id = request.form.get('post_id')
        commenter = request.form.get('commenter')
        comment_text = request.form.get('comment')
        if post_id and commenter and comment_text:
            post_comments = comments.get(post_id, [])
            new_comment = {"commenter": commenter, "comment": comment_text}
            post_comments.append(new_comment)
            comments[post_id] = post_comments
            save_comments(comments)

    post_with_comments = []
    for post in posts:
        post_comments = comments.get(str(post['id']), [])
        post_with_comments.append({"post": post, "comments": post_comments})

    return render_template('index.html', posts=post_with_comments)


# Like a post
@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if post:
        post['likes'] += 1
        save_posts(posts)
    return redirect(url_for('index'))


# View details of a single post
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if not post:
        return "Post not found", 404

    post_comments = comments.get(str(post_id), [])

    if request.method == 'POST':
        commenter = request.form.get('commenter')
        comment_text = request.form.get('comment')
        new_comment = {"commenter": commenter, "comment": comment_text}
        post_comments.append(new_comment)
        comments[str(post_id)] = post_comments
        save_comments(comments)

    return render_template('post.html', post=post, comments=post_comments)


# Add a new post
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        author = request.form.get('author')
        title = request.form.get('title')
        content = request.form.get('content')
        new_id = max(post['id'] for post in posts) + 1 if posts else 1
        posts.append({"id": new_id, "author": author, "title": title, "content": content, "likes": 0})
        save_posts(posts)
        return redirect(url_for('index'))
    return render_template('add.html')


# Delete a post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global posts
    posts = [post for post in posts if post['id'] != post_id]
    comments.pop(str(post_id), None)
    save_posts(posts)
    save_comments(comments)
    return redirect(url_for('index'))


# Update a post
@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if not post:
        return "Post not found", 404

    if request.method == 'POST':
        post['author'] = request.form.get('author')
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')
        save_posts(posts)
        return redirect(url_for('index'))

    return render_template('update.html', post=post)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
