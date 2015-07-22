from flask import Flask,render_template,url_for,request,redirect,flash,jsonify
app = Flask(__name__)

#visual database
blogs = [{'id':1,'title':'For test','content':'hello,world!','time':'1888-12-21'},
		{'id':2,'title':'For test2','content':'hello,world!2','time':'1892-10-20'},
		{'id':3,'title':'For test3','content':'hello,world!3','time':'1890-9-20'}]

@app.route('/')
@app.route('/hello')
def mainRage():
	return render_template('MyWeb.html')

@app.route('/blog')
def listBlog():
	return render_template('blogList.html',blogs = blogs)

@app.route('/blog/<int:blog_id>/read')
def readBlog(blog_id):
	blog = None
	for e in blogs:
		if e['id'] == blog_id:
			blog = e 

	if blog:	
		return render_template('readBlog.html',blog = blog)
	else:
		return 'sorry did not have it '

@app.route('/blog/new')
def newBlog():
	return render_template('newBlog.html')

if __name__ == '__main__':
	app.debug = True 
	app.run(host = '0.0.0.0' , port = 8080)
