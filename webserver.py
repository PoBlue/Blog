import re,hmac,random,string,hashlib
from time import strftime,localtime
from flask import Flask,render_template,url_for,request,redirect,flash,jsonify,make_response

app = Flask(__name__)

#sqlalchemy loaded 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Blog,Login

engine = create_engine('sqlite:///bolg.db')
Session = sessionmaker(bind=engine)
session = Session()

Logins = [{'id':1,'user_name':'rwer','pwd':'fajk'},{'id':2,'user_name':'hello','pwd':'fajk'},{'id':3,'user_name':'hello','pwd':'fajk'}]

#blog func
def valizBlog(title,content):
	if re.match(r'^[^ ]+',title) and re.findall('[^ \n\r\t]',content):
		return True
	else:
		return False

#make cookie and check fuc 
SECRET = 'hello,world'
def hash_str(s):
	return hmac.new(SECRET,s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s,hash_str(s))

def check_secure_val(h):
	if not h :
		return None

	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

#make hash password
def make_salt():
	return ''.join(random.choice(string.letters) for x in range(5))

def make_pw_hash(name,pw,salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name+pw+salt).hexdigest()
	return '%s,%s' % ( h,salt )

def valid_pw(name,pw,h):
	salt = h.split(',')[1]
	print make_pw_hash(name,pw,salt) == h
	return make_pw_hash(name,pw,salt) == h

@app.route('/blog/register',methods=['POST','GET'])
def register():
	if request.method == "POST":
		user_name = request.form['user_name']
		print user_name
		pwd = request.form['pw']
		apwd = request.form['apw']
		if pwd != apwd :
			return 'not same in twic'

		if not (user_name and pwd and apwd):
			return 'empty value'

		for e in Logins:
			print e
			if e.get('user_name') == user_name:
				return 'have this name'

		Logins.append({'user_name':user_name,'pwd':make_pw_hash(user_name,pwd)})

		rep = make_response(redirect(url_for('welcome',user_name=user_name)))
		rep.set_cookie('user_id',make_secure_val(user_name))

		return rep 
		
	return render_template('register.html')

@app.route('/blog/login',methods=['GET','POST'])
def login():
	print Logins
	if request.method == "POST":	
		user_name = request.form['user_name']
		pwd = request.form['pw']

		if not valizBlog(user_name,pwd):
			return 'empty pwd or user_name)'

		for e in Logins:
			print e.get('user_name'),user_name
			if e.get('user_name') == user_name:
				h = e.get('pwd')
				if valid_pw(user_name,pwd,h):
					rep = make_response(redirect(url_for('welcome',user_name=user_name)))
					rep.set_cookie('user_id',make_secure_val(user_name))
					return rep
				else:
					return 'pwd worng'

	return make_response(render_template('login.html')) 

@app.route('/blog/logout')
def logout():
	rep = make_response(redirect(url_for('login')))

	rep.set_cookie('user_id','')
	return rep

@app.route('/blog/<user_name>/welcome')
def welcome(user_name):
	user_cook = request.cookies.get('user_id')
	print type(user_cook)
	if check_secure_val(user_cook):
		return '<h1>welcome %s</h1>' % user_name
	
	return redirect(url_for('register'))
	

#blog page

@app.route('/hello')
def mainRage():
	print request.cookies
	print request.cookies.get('user')
	print request.headers
	return render_template('MyWeb.html')

@app.route('/')
@app.route('/blog')
def listBlog():
	blogs = session.query(Blog).all()
	return render_template('blogList.html',blogs = blogs)

@app.route('/blog/<int:blog_id>/read')
def readBlog(blog_id):
	blog = session.query(Blog).filter_by(id=blog_id).first()
	if blog:	
		return render_template('readBlog.html',blog = blog)
	else:
		return render_template('error.html',error='Sotty not have this blog')

@app.route('/blog/<int:blog_id>/edit',methods=['GET','POST'])
def editBlog(blog_id):
	blog = session.query(Blog).filter_by(id=blog_id).first()

	if blog:
		if request.method == 'POST':
			blog.title = request.form['title']
			blog.content = request.form['content']
			if valizBlog(blog.title,blog.content):
				session.add(blog)
				session.commit()

				flash('edit sucessful')
				return redirect(url_for('readBlog',blog_id=blog.id))
			else:
				flash('empty title or content')
				tmp = render_template('editBlog.html',blog=blog)
				session.rollback()

				return tmp

		return render_template('editBlog.html',blog=blog)
	else:
		return render_template('error.html',error='Sotty not have this blog')

@app.route('/blog/<int:blog_id>/delete',methods=['POST','GET'])
def deleteBlog(blog_id):
	blog = session.query(Blog).filter_by(id=blog_id).first()
	if blog:
		if request.method == 'POST':
			if request.form['flag'] == 'on':
				session.delete(blog)
				session.commit()
				return redirect(url_for('listBlog'))

			elif request.form['flag'] == 'off':
				return redirect(url_for('readBlog',blog_id=blog.id))
			else:
				return render_template('error.html',error='Bad Post')
				
		else:
			return render_template('deleteBlog.html',blog = blog)
	else:
		return render_template('error.html',error='Sotty not have this blog')

#test for study
@app.route('/test')
def Html():
	return render_template('test.html')

@app.route('/blog/new',methods=['GET','POST'])
def newBlog():
	blog = dict([('title',''),('content','')]) 
	if request.method == 'POST':
		blog['title'] = request.form['title']
		blog['content']  = request.form['content']
		time = strftime("%I:%M%p in %Y-%m-%d")
		if valizBlog(blog['title'],blog['content']):
			new = Blog(title=blog['title'],content=blog['content'],time=time)
			session.add(new)
			session.commit()
			flash('New Blog %s' % blog['title'])
			return redirect(url_for('listBlog'))
		else:
			flash('empty title or content')
			return render_template('newBlog.html',blog=blog)
	else:
		return render_template('newBlog.html',blog=blog)

if __name__ == '__main__':
	app.secret_key = 'mysecret'
	app.debug = True 
	app.run(host = '0.0.0.0' , port = 8080)
