import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, url_for, session, request
import os


app = Flask(__name__)

firebase_init = 0

import pyrebase
from flask import *
app = Flask(__name__)
app.secret_key = os.urandom(24)
config = {
	'apiKey': "AIzaSyD_ztd1-DlUWBFSNXTBWdYAnwus6WLOW0k",
	'authDomain': "tempit-initial.firebaseapp.com",
	'databaseURL': "https://tempit-initial.firebaseio.com",
	'projectId': "tempit-initial",
	'storageBucket': "tempit-initial.appspot.com",
	'messagingSenderId': "728716820991"
}

firebase = pyrebase.initialize_app(config)




@app.route('/')
def init():
	global firebase_init
	if firebase_init == 0:
		cred = credentials.Certificate('ServiceAccountKey.json')
		default_app = firebase_admin.initialize_app(cred, {
			'databaseURL' : 'https://tempit-initial.firebaseio.com'
			})
		firebase_init = 1
	return render_template('login.html')



@app.route('/authenticateUser',methods=['POST'])
def authenticateUser():
	username = request.form['uname']
	password = request.form['psw']
	print(username, password)
	auth = firebase.auth()
	try:  
		user = auth.sign_in_with_email_and_password(username, password)
		print("psuccess", username)
		
		uid = user['localId']
		print("success", username, uid)

	except:
		print('error with auth')
		return redirect('')

	if 'user' not in session:
		session['user'] = uid

	uid = session['user']
	curr_user = db.reference('userdb/').child(uid).get()
	if curr_user == None:
		return redirect('')


	return redirect(url_for('user_profile'))


@app.route('/authenticateCompany',methods=['POST'])
def authenticateCompany():
	username = request.form['uname']
	password = request.form['psw']

	try:
		user = firebase.auth().sign_in_with_email_and_password(username, password)
		uid = user['localId']
	except:
		print('error with auth')
		return redirect('')

	if 'user' not in session:
		session['user'] = uid

	uid = session['user']
	curr_company = db.reference('companydb/').child(uid).get()
	if curr_company == None:
		return redirect('')

	return redirect(url_for('employer_profile'))


@app.route('/newUser',methods=['POST'])
def newUser():
	fname = request.form['stu-fname']
	lname = request.form['stu-lname']
	email = request.form['stu-email']
	phone = request.form['stu-phone']
	psw = request.form['stu-psw']
	age = request.form['stu-age']
	skills = request.form['stu-skills']
	try:
		user = firebase.auth().create_user_with_email_and_password(email, psw)
		print("auth success")
	except:
		print('error with create user', email, psw)
		return redirect('')

	uid = user['localId']
	db = firebase.database()
	newData = {
		"fname": fname,
		"lname": lname,
		"email": email,
		"phone": phone,
		"psw": psw,
		"age": age,
		"skills": skills,
		"jobList": None
	}
	print(newData)
	db.child("userdb").child(uid).set(newData)
	print("created")
	if 'user' not in session:
		session['user'] = uid
	return redirect(url_for('user_profile'))

@app.route('/newCompany', methods=['POST'])
def newCompany():
	cname = request.form['cmp-cname']
	email = request.form['cmp-email']
	phone = request.form['cmp-phone']
	psw = request.form['cmp-psw']
	industry = request.form['cmp-industry']
	try:
		user = firebase.auth().create_user_with_email_and_password(email, psw)
	except:
		print('error with create user')
		return redirect('')
	uid = user['localId']
	db = firebase.database()
	newData = {
		"cname": cname,
		"email": email,
		"phone": phone,
		"psw": psw,
		"industry": industry,
		"jobList": None
	}
	db.child("companydb").child(uid).set(newData)
	if 'user' not in session:
		session['user'] = uid
	return redirect(url_for('employer_profile'))



@app.route('/user_profile')
def user_profile():
	global firebase_init
	if firebase_init == 0:
		cred = credentials.Certificate('ServiceAccountKey.json')
		default_app = firebase_admin.initialize_app(cred, {
			'databaseURL' : 'https://tempit-initial.firebaseio.com'
			})
		firebase_init = 1

	# users = db.reference('jobdb/').get()
	# uid = session['user']
	# email = users[uid]['email']
	uid = session['user']
	curr_user = db.reference('userdb/' + uid).get()

	return render_template('profile_card.html', email=curr_user['email'], 
		phone=curr_user["phone"], skills=curr_user['skills'].split(','))

@app.route('/employer_profile')
def employer_profile():
	global firebase_init
	if firebase_init == 0:
		cred = credentials.Certificate('ServiceAccountKey.json')
		default_app = firebase_admin.initialize_app(cred, {
			'databaseURL' : 'https://tempit-initial.firebaseio.com'
			})
		firebase_init = 1
	
	uid = session['user']
	curr_co = db.reference('companydb/').child(uid).get()

	return render_template('business_dash.html', name=curr_co['cname'], 
		email=curr_co["email"], industry=curr_co['industry'])

@app.route('/job_list')
def job_list():
	global firebase_init
	if firebase_init == 0:
		cred = credentials.Certificate('ServiceAccountKey.json')
		default_app = firebase_admin.initialize_app(cred, {
			'databaseURL' : 'https://tempit-initial.firebaseio.com'
			})
		firebase_init = 1
	#db = firebase.database()
	result = db.reference('jobsdb/').get()
	print(result)
	job_listing = result
	extracted_jobs = []
	i = 0
	for job in job_listing: 
		print(i)
		# schedule array
		#mp_times =str(job_listing[str(job)]['shift'])
		#print(str(job_listing[job]["shift"]))
		#print(type(job_listing[job]["startDate"]))
		#split = str(job_listing[job]["shift"]).split(' ')
		
		# print(job_listing[job]["shift"])

		# for ele in split:
		#tmp_el = job_listing[job]["shift"].split('-')
		#tmp_times = [(tmp_el[0], tmp_el[1])]

		temp = {"date": job_listing[job]["startDate"],
			'jobID': job,
			'image': "starbucks.png", #job_listing[job][imageURL]
			'title': job_listing[job]["title"],
			'description': job_listing[job]["description"], 
			#'pay': job_listing[job]["wage"], 
			'pay': job_listing[job]["wage"],
			'hours': job_listing[job]["totalHours"],
			'schedule': job_listing[job]["shift"]
		}
		extracted_jobs.append(temp)
		i = i + 1
	return render_template('job_list_tmplt.html', jobs=extracted_jobs)

@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('')

@app.route('/newListing',methods=['POST'])
def newListing():
	title = request.form['jl-title']
	totalHours = request.form['jl-totalHours']
	wage = request.form['jl-wage']
	startDate = request.form['jl-startDate']
	shift = request.form['jl-shifts']
	description = request.form['jl-description']
	companyId = session['user']

	db = firebase.database()
	newData = {
		"companyId": companyId,
		"title": title,
		"wage": wage,
		"totalHours": totalHours,
		"startDate": startDate,
		"shift": shift,
		"description": description,
		"taken": 0
	}
	newId = db.child("jobsdb").push(newData)
	db.child("companydb").child(companyId).child('jobList').push(newId)
	return redirect(url_for('employer_profile'))

@app.route('/chooseJob',methods=['POST'])
def chooseJob():
	jobId = request.form['jobId']
	uid = session['user']
	db = firebase.database()
	print("hello1")
	db.child("jobsdb").child(jobId).child('taken').set(1)
	db.child("jobsdb").child(jobId).child('userId').set(uid)
	db.child("userdb").child(uid).child('jobList').push(jobId)
	print("hello2")
	# comp = db.child("jobdb").child(jobId).child('companyId').get()
	print("hello3")
	#print(comp)
	# db.child("companydb").child(comp).child('jobList').child(jobId).push(uid)
	
	return redirect(url_for('user_profile'))
