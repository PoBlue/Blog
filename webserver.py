import re
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


@app.route('/blog/register')
def register():
	rep = make_response(render_template('register.html'))
	return rep

@app.route('/blog/login')
def login():
	rep = make_response(render_template('login.html')) 
	return rep

@app.route('/blog/logout')
def logout():
	return 'logout'

@app.route('/blog/<int:user_id>/welcome')
def welcome(user_id):
	return '<h1>welcome %i</h1>' % user_id

#blog page
def valizBlog(title,content):
	if re.match(r'^[^ ]+',title) and re.findall('[^ \n\r\t]',content):
		return True
	else:
		return False

@app.route('/')
@app.route('/hello')
def mainRage():
	return render_template('MyWeb.html')

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

@app.route('/blog/new',methods=['GET','POST'])
def newBlog():
	blog = dict([('title',''),('content','')]) 
	if request.method == 'POST':
		blog['title'] = request.form['title']
		blog['content']  = request.form['content']
		time = strftime("%Y-%m-%d %I:%M%p")
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
