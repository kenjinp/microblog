from flask import render_template, flash, redirect, session, url_for, request, g, make_response
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from config import CONFIG, POSTS_PER_PAGE
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, PostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post
from datetime import datetime

authomatic = Authomatic(CONFIG, 'your secret string', report_errors=False)

@lm.user_loader
def load_user(id):
        return User.query.get(int(id))

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
		db.session.add(post)
		print post
		db.session.commit()
		print "post commited to database"
		flash('Your post is now live! :D')
		return redirect(url_for('index'))

        posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False).items

	return render_template("index.html",
                title = 'Home',
                form = form,
		user = g.user,
                posts = posts)

#just a place to sign in
@app.route('/login', methods = ['GET', 'POST'])
def login():
        if g.user is not None and g.user.is_authenticated():
                flash("You're already logged-in, bustah!")
		return redirect(url_for('index'))
        form = LoginForm()
	print "user reached login form"
	return render_template('login.html', 
                title = 'Sign In',
		form = form,
                providers = app.config['PROVIDERS'])

#provide a spot to log-out!
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Successfully logged your ass out.')
	return redirect(url_for('index'))

#authentication
@app.route('/login/<provider_name>/',methods=['GET', 'POST'])
def auth(provider_name):
	print "user made response"
        response = make_response()
        result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
        if result:
		print "result has been made"
                if result.user:
                        result.user.update()
                #return redirect(request.args.get('next') or url_for('index', result == result))
		if result.user.email is None or result.user.email =="":
                	flash('Invalid Login. Please try again.')
                	return redirect(url_for('login'))
        	user = User.query.filter_by(email = result.user.email).first()
        	if user is None:
			print "user is none"
                	nickname = result.user.name
                	if nickname is None or nickname == "":
                        	nickname = result.user.email.split('@')[0]
                	nickname = User.make_unique_nickname(nickname)
			user = User(nickname = nickname, email = result.user.email, role = ROLE_USER)
                	db.session.add(user)
                	db.session.commit()
		#make the user follow him/herself
			db.session.add(user.follow(user))
			db.session.commit()
			print "put user in a database"
		print "trying to log user in"
		login_user(user)
		print "logged user in"
        	return redirect(url_for('index'))
	return response

@app.before_request
def before_request():
        g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/user/<nickname>')
@login_required
def user(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user == None:
		flash('User ' + nickname + ' not found.')
		return redirect(url_for('index'))
	posts = [
		{ 'author': user, 'body': 'Test post #1' },
		{ 'author': user, 'body': 'Test post #2' }
	]
	return render_template('user.html',
		user = user,
		post = posts)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return user(g.user.nickname)
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	
	return render_template('edit.html',
		form = form)

@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user == None:
		flash('User ' + nickname + 'not found. :(')
		return redirect(url_for('index'))
	if user == g.user:
		flash('You can\'t follow yourself!')
		return redirect(url_for('user', nickname = nickname))
	u = g.user.follow(user)
	if u is None:
		flash('Cannot follow ' + nickname +'. :(')
		return redirect(url_for('user', nickname = nickname))
	db.session.add(u)
	db.session.commit()
	flash('You are now following ' +nickname + '!')
	return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user == None:
		flash('User ' + nickname + ' not found.')
		return redirect(url_for('index'))
	if user == g.user:
		flash('You can\'t unfollow youself! >:O')
		return redirect(url_for('user', nickname = nickname))
	u = g.user.unfollow(user)
	if u is None:
		flash('Cannot unfollow ' + nickname + '. ;(')
		return redirect(url_for('user', nickname = nickname))
	db.session.add(u)
	db.session.commit()
	flash('You have stopped following ' + nickname + '.')
	return redirect(url_for('user', nickname = nickname))

#def after_login(resp):
#                remember_me = False
        #if 'remember_me' in session:
        #        remember_me = session['remember_me']
        #        session.pop('remember_me', None)
 #       login_user(user)
  #      return redirect(request.args.get('next') or url_for('index'))

