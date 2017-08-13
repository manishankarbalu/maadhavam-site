import codecs, os, pymongo
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from functools import wraps
from pymongo import MongoClient
import bcrypt
app = Flask(__name__)

MONGO_URL=os.environ.get('MONGODB_URI')
client=pymongo.MongoClient(MONGO_URL)
db=client.library
# Index
@app.route('/')
def index():
    return render_template('home.html',value='')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth/login',methods=['POST','GET'])
def login_template():
	#print 'entered login'
	users=db.users
	#print users
	login_user=users.find_one({'uname':request.form['uname']})
	if login_user :
		if bcrypt.hashpw(request.form['password'].encode('utf-8'),login_user['password'].encode('utf-8')) ==login_user['password'].encode('utf-8') :
			session['uname']=request.form['uname']
			session['logged_in']=True
			flash('You are now logged in', 'success')
			return redirect(url_for('dashboard'))
	return render_template('home.html',value='Invalid User Name or Password')		
	
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.route('/register', methods=['POST','GET'])
def regis():
	return render_template('register.html')

@app.route('/auth/register', methods=['POST','GET'] )
def register_template():
	#print 'rached'
	if request.method =='POST' and request.form['passkey']=="shankar":
		#print mongo
		users=db['users']
		#print users
		existing_user=users.find_one({'uname':request.form['uname']})
		#print existing_user
		if existing_user == None:
			hashpass=bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
			print hashpass,users
			db['users'].insert({'uid':request.form['uid'],'name':request.form['name'],'uname':request.form['uname'],'password':hashpass,'phone':request.form['phone']})
			session['uname']=request.form['uname']
			print 'inserted'
			return 'registerd as '+request.form['name']
			return render_template('login.html')
	return render_template('home.html',value="Invalid Passkey Contact maadhavam")

@app.route('/post')
@is_logged_in
def post():
	return render_template('fillpost.html')


@app.route('/add/posts',methods=['POST','GET'])
@is_logged_in
def add_post():
	if request.method=="POST":
		post=db['posts']
		post.insert({'title':request.form['title'],'desc':request.form['desc'],'author':request.form['author']})
		return redirect(url_for('article'))


# About
@app.route('/about')
@is_logged_in
def about():
	content=db['content']
	v=content.find({})
	s=[]
	for i in v:
		s.append(i)
	print  s
	return render_template('about.html',values=s)


@app.route('/article')
def article():
	pst=db['posts']
	l=[]
	v=pst.find({})
	for i in v:
		l.append(i)
	return render_template('article.html',articles=l)


if __name__ == '__main__':
	app.secret_key = 'secretkey'
	app.run(debug=True)
