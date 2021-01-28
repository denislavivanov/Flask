from flask import *
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
import datetime

username = ""
password = ""

app = Flask("Forum")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super secret key"

db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(100), nullable=False)

	def __init__(self, username, password):
		self.username = username
		self.password = password

class Topic(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	author = db.Column(db.String(50), nullable=False)
	date = db.Column(db.String(20), nullable=False)

	def __init__(self, title, author, date):
		self.title = title
		self.author = author
		self.date = date

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	topic = db.Column(db.String(50), nullable=False)
	title = db.Column(db.String(50), nullable=False)
	author = db.Column(db.String(50), nullable=False)
	date = db.Column(db.String(20), nullable=False)
	content = db.Column(db.String(1000), nullable=False)

	def __init__(self, topic, title, author, date, content):
		self.topic = topic
		self.title = title
		self.author = author
		self.date = date
		self.content = content

class Current_Topic(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)

	def __init__(self, title):
		self.title = title

def login_check(users, username, password):
	for user in users:
		if user.username == username and user.password == password:
			return True

	return False

def user_posts(posts, author):
	p = []
	for post in posts:
		if post.author == author:
			p.append(post)

	return p

def topic_posts(posts, topic):
	p = []
	for post in posts:
		if post.topic == topic:
			p.append(post)

	return p

def remove_post(posts, title, author, topic):
	for post in posts:
		if post.title == title and post.author == author and post.topic == topic:
			posts.remove(post)

db.create_all()

topics = Topic.query.all()
posts = Post.query.all()

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])

def home():
	if request.method == 'POST':
		logout = request.form.get('logout')
		title = request.form.get('title')
		topic = request.form.get('topic-title')
		post = request.form.get('post')
		delete = request.form.get('delete')

		if delete:
			current_topic = Current_Topic.query.all()[0].title
			remove_post(posts, delete, session['name'], current_topic)
			db.session.query(Post).filter(Post.title==delete, Post.author==session['name'], Post.topic==current_topic).delete()
			db.session.commit()
			
			u_posts = user_posts(posts, session['name'])
			t_posts = topic_posts(posts, current_topic)

			delete = len(u_posts)

			return render_template('topic.html', username=session['name'], loggedin=True, topic=current_topic, user_posts=u_posts, posts=t_posts, delete=delete)
		
		if topic:
			db.session.query(Current_Topic).filter(Current_Topic.id == 1).delete()
			new_topic = Current_Topic(topic)
			db.session.add(new_topic)
			db.session.commit()

			t_posts = topic_posts(posts, topic)

			if "loggedin" in session:
				u_posts = user_posts(posts, session['name'])
				delete = len(u_posts)
				return render_template('topic.html', username=session['name'], loggedin=True, topic=topic, user_posts=u_posts, posts=t_posts, delete=delete)
			else:
				return render_template('topic.html', username="", loggedin=False, topic=topic, posts=t_posts, delete=False)

		if post:
			current_topic = Current_Topic.query.all()[0].title
			now = datetime.datetime.now()
			time = datetime.datetime.strftime(now, '%d-%m-%Y %H:%M')
			
			p = Post(current_topic, title, session['name'], time, post)
			posts.append(p)
			db.session.add(p)
			db.session.commit()

			u_posts = user_posts(posts, session['name'])
			t_posts = topic_posts(posts, current_topic)

			delete = len(u_posts)

			return render_template('topic.html', username=session['name'], user_posts=u_posts, loggedin=True, topic=current_topic, posts=t_posts, delete=delete)

		if title:
			now = datetime.datetime.now()
			time = datetime.datetime.strftime(now, '%d-%m-%Y %H:%M')

			t = Topic(title, session['name'], time)
			topics.append(t)
			db.session.add(t)
			db.session.commit()

			return render_template('home.html', username=session["name"], loggedin=True, topics=topics)

		if logout and "loggedin" in session:
			session.pop('name')
			session.pop('loggedin')
			
		return render_template('home.html', username="", loggedin=False, topics=topics)

	if request.method == 'GET':
		if "loggedin" in session:
			return render_template('home.html', username=session["name"], loggedin=True, topics=topics)
		else:
			return render_template('home.html', username="", loggedin=False, topics=topics)


@app.route('/about', methods=['GET', 'POST'])
def about():
	if request.method == 'POST':
		logout = request.form.get('logout')
		if logout:
			session.pop('name')
			session.pop('loggedin')
		return render_template('about.html', username="", loggedin=False)

	if request.method == 'GET':
		if "loggedin" in session:
			return render_template('about.html', username=session["name"], loggedin=True)
		else:
			return render_template('about.html', username="", loggedin=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		session['name'] = str(request.form.get('user'))
		username = sha256(session['name'].encode("utf-8")).hexdigest()
		password = sha256(request.form.get('pass').encode("utf-8")).hexdigest()

		if login_check(User.query.all(), username, password): 
			session['loggedin'] = True
			return redirect(url_for("home"))
		else:
			return render_template('login.html', error=1)

	if request.method == 'GET':
		return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = sha256(request.form.get('user').encode("utf-8")).hexdigest()
		password = sha256(request.form.get('pass').encode("utf-8")).hexdigest()
		confirm_password = sha256(request.form.get('c_pass').encode("utf-8")).hexdigest()

		if password != confirm_password:
			return render_template('register.html', error=1)

		user = User(username, password)

		db.session.add(user)
		db.session.commit()

		return render_template('register.html', error=0)

	if request.method == 'GET':
		return render_template('register.html')

app.run(debug=True)

