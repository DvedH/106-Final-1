
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import request
from flask import abort, render_template, redirect, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from enum import Enum
from urllib.parse import parse_qs
from urllib.parse import urlparse
import bcrypt
import sys
import json

app = Flask(__name__)
app.secret_key = 'super secret key'

with app.app_context():
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(username="ansony3",password="testpack",hostname="ansony3.mysql.pythonanywhere-services.com",databasename="ansony3$forum_db_dec6",)
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    admin = Admin(app, name='microblog', template_mode='bootstrap3')
    db = SQLAlchemy(app)


    class Users(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userID = db.Column(db.String(500), unique=True, nullable=False)
        password = db.Column(db.String(500), unique=False, nullable=False)

    class forumID(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        tag = db.Column(db.String(500), unique = True, nullable = False)

    class ForumPost(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userID = db.Column(db.String(500), unique=False, nullable=False) #This is to mark who is the original poster.
        text = db.Column(db.String(500),nullable = False) #This is where the text post is....
        tag = db.Column(db.String(500), nullable = False) #This is to set what tag the post could be.
        time = db.Column(db.String(500),nullable = False) #This is to show the time the post was made?
        score = db.Column(db.String(500), nullable = True) #This is to show upvote or downvotes.

    class ForumReply(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userID = db.Column(db.String(500), unique=False, nullable=False) #This is to mark who is the original poster.
        text = db.Column(db.String(500),nullable = False) #This is where reply should be
        tag = db.Column(db.String(500), nullable = False) #This is to set what tag the post could be. This could be optional.
        time = db.Column(db.String(500),nullable = False) #This is to show the time the post was made?
        score = db.Column(db.Integer, nullable = True) #This shows upvote and downvote.
        recipient = db.Column(db.String(500), nullable = False) #This should show the person you are replying to

    class Topic(Enum):
        videogames = 1
        anime = 2
        none = 3

    #Initialize database and classes
    db.create_all()
    admin.add_view(ModelView(Users, db.session))
    admin.add_view(ModelView(ForumPost, db.session))
    admin.add_view(ModelView(ForumReply, db.session))
    admin.add_view(ModelView(forumID,db.session))


    @app.route('/')
    def start():
        return render_template('register.html')


    # Routing of website routes are below.
    @app.route('/login', methods=['POST'])  # Login page
    def login():
        name = request.form['usn']
        pswd = request.form['psw']

        user = Users.query.filter_by(userID=name).first()

        if not user:
            return render_template('login.html', info="wrong Username")
        if bcrypt.checkpw(pswd.encode('utf8'), user.password.encode('utf8')):
            session["user"] = name
            return redirect('/homePage')
        else:
            return render_template('login.html', info="wrong Password")


    @app.route('/register', methods=['POST'])  # Show register page
    def register():
        usn = request.form['usn']
        pswd = request.form['psw']
        new = True
        if Users.query.filter_by(userID=usn).first():
            check = Users.query.filter_by(userID=usn).first()
            print(check.userID)
            new = False

        if not usn:
            return render_template('register.html', info="Please provide an Username")

        if not pswd:
            return render_template('register.html', info="Please provide a password")

        if not new:
            if check.userID == usn:
                return render_template('register.html', info="This Username is already taken")

        hashed = bcrypt.hashpw(pswd.encode('utf8'), bcrypt.gensalt())

        db.session.add(Users(userID=usn, password=hashed))
        db.session.commit()
        return render_template('login.html', info="Welcome " + usn + "!")


    @app.route('/loginRedirect', methods=['GET'])
    def lRedir():
        return render_template("/login.html")


    @app.route('/LookAtThread', methods=['POST'])
    def discussion():
        username = session["user"]
        result = ForumPost.query.all()
        search = request.form['Post']
        print(search)
        find = {}
        counter = 0
        c = 0;
        if not search:
            return render_template('HomePage.html', name=username, error="type something to search for it")

        for i in result:
            counter += 1

        for h in result:
            if search == h.text:
                c += 1
                usrname = h.userID
                time = h.time
                tags= h.tag
                id = h.id

                print(usrname)
                print(time)
                print(tags)

        if c == 1:
            return render_template('Thread.html', YOU=username, postID=id, OPUsername=usrname, Time=time, Tags=tags, OpText=search)
        else:
            return render_template('HomePage.html', name=username, error="Couldn't find the post")

    @app.route('/registerRedirect', methods=['GET'])
    def rRedir():
        return render_template("/register.html")


    @app.route('/homePage')
    def homePage():
        username = session["user"]
        return render_template('HomePage.html', name=username)


    @app.route('/FillTags', methods=["GET"])
    def fill():
        result = forumID.query.all()
        counter = 0;
        for i in result:
            counter +=1
        tags = {}

        for r in range(0,counter):
            tags[r] = {}
            tags[r]["tag"] = result[r].tag

        print(session["user"])
        return tags
    #USER FUNCTIONS

    #Allow user to make a post on a forum board.
    #When sending an AJAX request, please send in: username: , text: , tags:
    @app.route('/<string:username>/post', methods = ['GET','POST'])
    def PostOnForum(username):
        #Query all users & content from the post method.
        contents = request.get_json(silent=True)
        print(contents)
        userPost = Users.query.all()
        #Find if this is a valid user so they can post.
        result = db.session.execute(db.select(Users.userID).where(Users.userID == username))
        #If the username from result matches the username argument, allow them to post
        if(result.first().userID == username):
            #Start the post operation.
            #Create new forum thread/post using the ForumPost class.
            db.session.add(ForumPost(userID = contents["username"], text = contents["text"], tag = contents["tags"] , time = datetime.now(), score = 0))
            #Commit to forum's database.
            db.session.commit()


        return ""

    #Show all posts.
    @app.route('/showPosts/<string:tag>', methods=['POST'])
    def getPosts(tag):

        results = ForumPost.query.all()
        counter = 0;
        posts = {}
        print(tag)

        for h in results:
            if tag in h.tag:
                counter += 1
                posts[counter] = h.text

        print(posts)

        '''
        animeURL = request.url
        print(animeURL)

        parsed_animeURL = urlparse(animeURL)
        query_string = parsed_animeURL.query
        query_var = parse_qs(query_string)
        print(query_var)
        print("printed query_var")

        if ("tags" in query_var):
            taggedPost = query_var["tag"]
        else:
            taggedPost = ""

        print(taggedPost)
        print("tagged post")

        allPosts = ForumPost.query.all()
        tag_var = taggedPost.pop()
        posts = {}
        for i in allPosts:
            if (tag_var == "" or tag_var in i.tag):
                posts[i.id] = i.text
        print (posts)
        return posts'''
        return posts


    @app.route('/showAllPosts', methods = ['GET'])
    def getAllPosts():
        print("hello")
        queuedPosts = ForumPost.query.all()
        posts = {}
        for i in queuedPosts:
            posts[i.id] = i.text
            print (i.id)
            print(i)

        print(posts)
        return posts

    #Show threads -> This is just making a new link, showing the post, and then including the ability to make a forumReply
    @app.route('/getThread/<string:id>',methods = ['GET'])
    def threads(id):
        #Render the html and call the post id?
        #------------actual function below-------------------#
        #Get the id of ForumPost that matches the id in the route. /thread/1 would load up the page with the first post.
        threadPost = db.session.execute(db.select(ForumPost.text).where(ForumPost.id == id))
        #ChunkedIterator is a pain, so we convert it into a dictionary.
        threadDictionary = [dict(r) for r in threadPost.all()]
        #Iterate
        for threadDict in threadDictionary:
            threadDict["text"]
        return threadDict["text"]





    #Allow user to reply to a post.
    @app.route('/<string:username>/<string:threadID>/forumReply', methods = ['POST']) #Username is the person sending the message, poster is the person who will receive the response
    def ReplyToUser(username,threadID):
        #Load up contents, from the frontend
        contents = request.get_json(silent=True) #This is where the stuff from the textbox gets sent to.
        #Make sure only valid users can post a reply...
        result = db.session.execute(db.select(Users.userID).where(Users.userID == username))
        #If the username from result matches the username argument, allow them to post the reply
        if(result.first().userID == username):
            #Start the post operation.
            #Create a new thread reply using the ForumReply class.
            db.session.add(ForumReply(userID = contents["username"], text = contents["text"], tag = "none" , time = datetime.now(), score = 0, recipient = threadID)) #Tag will be set to none, it actually has no purpose here.
            #Commit to forum's database.
            db.session.commit()

        return "pass"

    #This will show all of the replies for each thread!
    @app.route('/showReply/<string:threadID>', methods = ['GET'])
    def ShowThreadReplies(threadID):
        print(threadID)
        #Queue up all of the forum replies.
        threadReply = ForumReply.query.all()
        replies = {}
        counter = 0
        # From this class, we will find all of the replies that have the same threadID
        # Add all replies that match.
        for i in threadReply:
            if (threadID == i.recipient):
                counter+=1
                replies[counter] = {}
                replies[counter]["User"] = i.userID
                replies[counter]["Message"] = i.text

        print(replies)
        return replies

    #Allow user to upvote a post -- RAN OUT OF TIME FOR DEVELOPMENT
    #@app.route('/getThread/<string:id>/upvotePost', methods = ['PUT'])
    #def upvotePost(id):
    #    #Find the target post
    #    contents = request.get_json(silent = True)
    #    targetPost = ForumPost.query.filter_by(id=contents["postID"]).first()
    #    targetScore = targetPost.score
     #   #Make sure the post being upvoted is a valid post.
     #   newScore = ForumPost.query.filter_by(id=contents["postID"]).update(dict(score = targetScore + 1) )
    #    db.session.commit()

        return ""


