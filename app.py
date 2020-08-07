#required importds to connect to sqlite database
import sqlite3
# g is used for database
from flask import Flask, render_template, request, session, redirect, url_for, escape, flash, g

DATABASE='./assignment3.db'


#other function get_db is taken from here
def get_db():
	db=getattr(g, '_database', None)
	if db is None:
		db=g._database=sqlite3.connect(DATABASE)
	return db


def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return(rv[0] if rv else None) if one else rv


def make_dicts(cursor, row):
	return dict((cursor.description[idx][0], value)
					for idx, value in enumerate(row))


app = Flask(__name__)

app.secret_key=b'azeem'

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()


@app.route('/')
def home():
	#This is to ensure that the user stays logged in.
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		# Once the user is logged in, make sure to direct them to the Home page of the website
		return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
	#Aqquire the databse
	db=get_db()
	db.row_factory = make_dicts

	#Get the username and the password
	attempted_username= request.form['username']
	attempted_password= request.form['password']

	#perform a query check to see if password and username are present in db 
	check_login=query_db('SELECT * from Login where username = ? and password=?',[attempted_username, attempted_password],one=True)
	
	if check_login is None:
		#If username and password fail to be available, just flash username and password are wrong and return them to home
		flash("username does not exist")
		return home()
	#Check if the password and username are present and match
	elif request.form['password'] == check_login['password'] and request.form['username'] == check_login['username']:
		#Aqquire the userType and Sid of user as they will be usefull throughout the program
		new_Type = query_db('SELECT userType from Login where username = ? and password=?',[attempted_username, attempted_password],one=True)
		new_Sid = query_db('SELECT Sid from Login where username = ? and password=?',[attempted_username, attempted_password],one=True)
		session['logged_in'] = True
		session['userType']= new_Type['userType']
		session['Sid']= new_Sid['Sid']
	db.close()
	return home()


@app.route("/logout")
def logout():
	session['logged_in'] = False
	flash("You have been logged out!", "info")
	return home()



@app.route('/register', methods=['GET','POST'])
def register():
	# Check if the request method is POST
	if (request.method == "POST"):
		#Aqquire database
		db = get_db()
		db.row_factory = make_dicts
		
		#Set ALL the user info into variables so its easier to put into query
		new_username= request.form['username']
		new_password= request.form['password']
		new_Sid= request.form['Sid']
		new_fname= request.form['Fname']
		new_lname= request.form['Lname']
		new_type= request.form['user_type']

		#check for duplicates
		check_user=query_db('SELECT * from Login where username = ? or Sid = ?', [new_username, new_Sid])
		if len(check_user) > 0:
			#if duplicate user exists, flash the following message
			flash("User already exists")
			return render_template('register.html')
		else:
			#Create a cursor obj
			cur = db.cursor()

			#Do an execute method to insert the user info into db
			cur.execute('INSERT INTO Login (username,password,Sid,FirstName,LastName,userType) VALUES (?,?,?,?,?,?)', [new_username,new_password,new_Sid,new_fname,new_lname,new_type])
			
			# IF user is a student, create an additional row for him in the grades table (Teacher will fill out on later date)
			if new_type == "student":
				cur.execute('INSERT INTO Grades (StudentID) VALUES (?)', [new_Sid])
			
			#Set session to logeed in and aqquire the userType and Sid
			session['logged_in'] = True
			session['userType']= new_type
			session['Sid']= new_Sid
			db.commit()
			cur.close()
		db.close()
		return home()
	else:
		return render_template('register.html')



@app.route('/syllabus')
def syllabus():
	return render_template('syllabus.html')


@app.route('/labs')
def labs():
	return render_template('lab.html')

@app.route('/lectures')
def lectures():
	return render_template('lectures.html')


@app.route('/team')
def team():
	return render_template('team.html')


@app.route('/anonFeedback', methods=['GET','POST'])
def anonFeedback():
	#check the userType 
	if session['userType'] == 'student':
		# if method is GET, then we just display the actual form
		if(request.method == "GET"):
			db = get_db()
			db.row_factory = make_dicts

			#Create a dict and then populate it with data from the db
			Instructors=[]
			new_userType="instructor"
			for instruct in query_db('SELECT * from Login where userType = ?',[new_userType]):
				Instructors.append(instruct)
			db.close()
		# if method is POST, then we just insert everything into the database
		elif(request.method == "POST"):
			db = get_db()
			db.row_factory = make_dicts

			#Add everything to variables so its easier to put into db
			new_Sid= request.form['Sidmsg']
			new_msg1= request.form['message1']
			new_msg2= request.form['message2']
			new_msg3= request.form['message3']
			new_msg4= request.form['message4']

			#Create a cursor function and then execute func by inserting data in anonfeedack table
			cur = db.cursor()
			cur.execute('INSERT INTO anonFeedback (Sid,Q1,Q2,Q3,Q4) VALUES (?,?,?,?,?)', [new_Sid, new_msg1, new_msg2, new_msg3, new_msg4])
			session['logged_in'] = True
			db.commit()
			cur.close()
			db.close()
			#return a render template to home page
			return home()
		return render_template('anonFeedback.html', instructor=Instructors)
	else:
		#Aqquire the database
		db = get_db()
		db.row_factory = make_dicts

		#Get the sid of the logged in user
		new_Sid=session['Sid']

		#Create a dict and populate it with the feedback meant for the logged in user
		allFeedbacks=[]
		for feedback in query_db('SELECT * from anonFeedback where Sid = ?',[new_Sid]):
			allFeedbacks.append(feedback)
		#Check if the instuctor had any Feedback or not 
		if not allFeedbacks:
			flash("You have no Reviews")
		db.close()
		return render_template('anonFeedbackInstructor.html', instructor=allFeedbacks)
	return render_template('anonFeedbackInstructor.html', instructor=Instructors)


@app.route("/gradeTable", methods=['GET','POST'])
def gradeTable():
	if (request.method == "POST"):
		db = get_db()
		db.row_factory = make_dicts

		#Add everything to variables so its easier to put into db

		new_Sid= session['placeholderSid']
		new_A1= request.form['A1']
		new_A2= request.form['A2']
		new_A3= request.form['A3']
		new_Midterm= request.form['Midterm']
		new_Final= request.form['Final']

		#Create a cursor function and then execute func by inserting data in anonfeedack table
		cur = db.cursor()
		cur.execute('UPDATE Grades set A1=?, A2=?, A3=?, Midterm=?, Final=? where StudentID=?', [new_A1, new_A2, new_A3, new_Midterm, new_Final, new_Sid])
		db.commit()
		cur.close()
		db.close()
		flash("Marks Updated")
		#return a render template to home page
	return home()

@app.route('/studentGradeChange', methods=['GET','POST'])
def studentGradeChange():
	if(request.method == "POST"):
		#Aqquire the databases
		db=get_db()
		db.row_factory = make_dicts

		#Get the students Sid
		student_Sid= request.form['StudentID']
		session['placeholderSid']= student_Sid

		#Input query where we select the student where Sid  matches the input query
		student=query_db('select * from Grades where StudentID = ?', [student_Sid], one=True)
		db.close()
		return render_template('gradeChange.html', student=[student])
		#implement mark changing code here 
	return render_template('gradeChange.html') 


@app.route('/Grades', methods=['GET','POST'])
def Grades():
	#check the userType 
	if session['userType'] == 'student':
		#Aqquire the databases
		db=get_db()
		db.row_factory = make_dicts

		#Get the students Sid
		student_Sid= session['Sid']

		#Input query where we select the student where Sid  matches the input query
		student=query_db('select * from Grades where StudentID = ?', [student_Sid], one=True)
		db.close()
		return render_template('testStudent.html', student=[student])

	else:
		#Aqquire the database
		db=get_db()
		db.row_factory = make_dicts

		#Create student Database and populate it with all the students
		Students=[]
		for student in query_db('select * from Grades'):
			Students.append(student)
		db.close()
		return render_template('test.html', student=Students)
	return render_template("test.html")



@app.route('/remarkStudent', methods=['GET','POST'])
def remarkStudent():
	if(request.method == "POST"):
		#Check the login type of user
		if session['userType'] == "student":
			#Aqquire the database
			db=get_db()
			db.row_factory = make_dicts

			#Get the values to be put into the remark request table 
			new_Assign=request.form['AssName']
			new_Sid = session['Sid']
			new_request= request.form['Reason']

			#create a cursor variable and execute to insert data into the table 
			cur = db.cursor()
			cur.execute('INSERT INTO remarkRequest (Sid,AssignName,Reason) VALUES (?,?,?)', [new_Sid, new_Assign, new_request])
			db.commit()
			cur.close()
			db.close()
			flash("Request Sent")
	return home()


@app.route('/remarkRequest', methods=['GET','POST'])
def remarkRequest():
	#check user type
	#if(request.method == "POST"):
	#Check the login type of user
	if session['userType'] == "student":
		#Aqquire the databases
		db=get_db()
		db.row_factory = make_dicts

		#Get the students Sid
		student_Sid= session['Sid']

		#Input query where we select the student where Sid  matches the input query
		student=query_db('select * from remarkRequest where Sid = ?', [student_Sid], one=True)
		db.close()
		return render_template('studentRemark.html', studentrequest=[student])
	else:
		#Aqquire data type
		db=get_db()
		db.row_factory = make_dicts

		#Create dict and insert all the requests into said dict from db
		remarkRequests=[]
		for remark in query_db('SELECT * from remarkRequest'):
			remarkRequests.append(remark)
		db.close()
		return render_template('remarkRequest.html', request=remarkRequests)
		#return render_template('remarkRequest.html')

	

if __name__ == "__main__":
	app.run(debug=True)