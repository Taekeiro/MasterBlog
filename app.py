from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# JSON file to store blog posts
DATA_FILE = 'blog_posts.json'

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

# Initial posts loaded from the file
posts = load_posts()

# Homepage: List all blog posts
@app.route('/')
def index():
    return render_template('index.html', posts=posts)

# View details of a single post
@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if not post:
        return "Post not found", 404
    return render_template('post.html', post=post)

# Add a new post
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        author = request.form.get('author')
        title = request.form.get('title')
        content = request.form.get('content')
        new_id = max(post['id'] for post in posts) + 1 if posts else 1
        posts.append({"id": new_id, "author": author, "title": title, "content": content})
        save_posts(posts)
        return redirect(url_for('index'))
    return render_template('add.html')

# Delete a post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global posts
    posts = [post for post in posts if post['id'] != post_id]
    save_posts(posts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
