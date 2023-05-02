from flask import Flask, render_template, redirect, url_for, request, jsonify,make_response,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some_secret_key'
db = SQLAlchemy(app)
app.app_context().push()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(20) ,nullable=False)
    password = db.Column(db.String(60), nullable=False)
    interest= db.Column(db.String(200), nullable=False)
    preference= db.Column(db.String(200), nullable=False)
    

    def __repr__(self):
        return f'User({self.username})'
 

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Module('{self.name}', '{self.credits}')"

# enrollment
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20),  unique=True,nullable=False)
    enrolled_course = db.Column(db.String(500))
    

    def __repr__(self):
        return f"Enrollment('{self.Studentid}', '{self.name}','{self.email}')"

@app.route('/')
def index():
    value=None
    try:
        value=session['value']
        print(value)
    except:
        print(value)    
    return render_template('index.html',value=value)

@app.route('/logout')
def logout():
    session['value']=None
    return render_template('index.html',value=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None:
            error = 'Invalid username or password. Please try again.'
        elif not check_password_hash(user.password, password):
            error = 'Invalid username or password. Please try again.'
        else:
            session['value']=user.username;
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/enrollment')
def enrollment():
    file1 = open("modules.txt", "r")
    collection=file1.read()
    final=json.loads(collection)

    username=session.get('value');
    user = User.query.filter_by(username=username).first()
    usersall = User.query.all()
    interest=json.loads(user.interest)
    interestarr=[]
    interestarrType=[]
    file1.close()
    filterEnrollment=Enrollment.query.all()
    UsernameEnrollment=Enrollment.query.filter_by(email=user.email).first()

    
   

    for i in final:
        if len(filterEnrollment)>0:
            if(i['rateNumber']>0):
                i['rating']=int(i['rateNumber']*100/len(filterEnrollment))
            else:
                i['rating']=0
        else:
                i['rating']=0
        
  
    for i in interest:
        for j in final:
            for k in j.get('type'):
                if(k==i):
                    if(k not in interestarrType):
                        interestarrType.append(k)
                    interestarr.append(j)
    for i in final:
        if(i.get('preference').lower()==user.preference.lower()):
            interestarr.append(i)

    newinterestarr=[]
    for j in interestarr:        
        # print(j['type'])
        if j['rating'] >= 80:
            if j['preference'].lower()==user.preference.lower():
                strType=""
                interestFound=False
                check=[]
                for i in j['type']:
                    if(i in interestarrType):
                        strType+=f"{i} and "
                        check.append(i)
                strType=strType[:-5]
                interestinner=json.loads(user.interest)
                for innerchecking in interestinner:
                
                    if innerchecking.lower() in j['type']:
                        interestFound=True
                
                if interestFound==True:
                    if (len(check)>1):
                        if j['preference'].lower()=="both":
                            j['choose']=f"Because you picked {strType} as your interests. You also picked both standard and coursework exams, as your preference."
                        else:
                            j['choose']=f"Because you picked {strType} as your interests. You also picked {j['preference']} as your preference."
                    else:
                        if j['preference'].lower()=="both":
                            j['choose']=f"Because you picked {strType} as one of your interests. You also picked both, standard and coursework exams, as your preference."
                        else:
                            j['choose']=f"Because you picked {strType} as one of your interests. You also picked {j['preference']} as your preference."
                else:
                    if j['preference'].lower()=="both":
                        j['choose']=f"Because you picked standard and coursework exams as your preference."
                    else:
                        j['choose']=f"Because you picked {j['preference']} as your preference."
            else:
                strType=""
                check=[]
                for i in j['type']:
                    if(i in interestarrType):
                        strType+=f"{i} and "
                        check.append(i)
                strType=strType[:-5]
                if(len(check)>1):
                    j['choose']=f"Because you picked {strType} as your interests."
                    
                else:
                    j['choose']=f"Because you picked {strType} as one of your interests."
            if len(usersall)>5:
                j['choose']+=f" The majority of students have enrolled in this module."
        elif j['preference'].lower()==user.preference.lower():
            
            strType=""
            interestFound=False
            check=[]
            for i in j['type']:
                if(i in interestarrType):
                    strType+=f"{i} and "
                    check.append(i)
            strType=strType[:-5]
            interestinner=json.loads(user.interest)
            for innerchecking in interestinner:
              
                if innerchecking.lower() in j['type']:
                    interestFound=True
            
            if interestFound==True:
                if (len(check)>1):
                    if j['preference'].lower()=="both":
                        j['choose']=f"Because you picked {strType} as your interests. You also picked both, standard and coursework exams, as your preference."
                    else:
                        j['choose']=f"Because you picked {strType} as your interests. You also picked {j['preference']} as your preference."
                else:
                    if j['preference'].lower()=="both":
                        j['choose']=f"Because you picked {strType} as one of your interests. You also picked both, standard and coursework exams, as your preference."
                    else:
                        j['choose']=f"Because you picked {strType} as one of your interests. You also picked {j['preference']} as your preference."
            else:
                if j['preference'].lower()=="both":
                    j['choose']=f"Because you picked standard and coursework exams as your preference."
                else:
                    j['choose']=f"Because you picked {j['preference']} as your preference."
        else:
            strType=""
            check=[]
            for i in j['type']:
                if(i in interestarrType):
                    strType+=f"{i} and "
                    check.append(i)
            strType=strType[:-5]
            if(len(check)>1):
                j['choose']=f"Because you picked {strType} as your interests."
            else:
                j['choose']=f"Because you picked {strType} as one of your interests."
            


        inc=0
        iterate=0
        for i in interestarr:
            # print(i)
            if i not in newinterestarr:
                newinterestarr.append(i)
    jsonData=None
    if UsernameEnrollment != None:
        jsonData=json.loads(UsernameEnrollment.enrolled_course)
    for i in final:
        if len(usersall)>5:
            if(i.get('rating')>=80):
                if(i in newinterestarr):
                    pass
                else:
                    i['choose']="Because the majority of students have enrolled in this module."
                    newinterestarr.append(i)
                
        


    return render_template('enrollment.html', modules=final,interestarr=newinterestarr,jsonData=jsonData)

@app.route('/enrollment_submit', methods=['POST'])
def enrollment_submit():
    file1 = open("modules.txt", "r")
    collection=file1.read()
    modules=json.loads(collection)
    enrolled = request.form.get('student_details')
    modulesSession=json.loads(session.get('modules_arr'))
    enrolled = json.loads(enrolled)
    record=Enrollment(name=enrolled.get('name'),email=enrolled.get('email'),enrolled_course=enrolled.get('EnrolledHidden'))
    filterarr=[]
    filterEnrollment=Enrollment.query.all()

   
    for i in modulesSession:
        for j in modules:
            if(i==j.get('code')):
                j['rateNumber']=j['rateNumber']+1
                
    file1.close()
    file1 = open("modules.txt", "w")
    file1.write(json.dumps(modules))
    db.session.add(record)
    db.session.commit()
    return render_template('EnrollmentDone.html')

@app.route('/confirmation', methods=['POST'])
def confirmation():
    file1 = open("modules.txt", "r")
    collection=file1.read()
    modules=json.loads(collection)
    enrolled_modules = request.form.get('enrolled_modules')
    
    enrolled_modules = json.loads(enrolled_modules)
    enrolled_modulesnewAgain=[]
    print(enrolled_modules)
    for i in enrolled_modules:
        if i in enrolled_modulesnewAgain:
            pass
        else:
            enrolled_modulesnewAgain.append(i)
    enrolled_modules=enrolled_modulesnewAgain
    enrolled_modules_array=[]
    session['modules_arr']=json.dumps(enrolled_modules)
    filterEnrollment=Enrollment.query.all()
    print(enrolled_modules)
    username=session.get('value');
    user = User.query.filter_by(username=username).first()
    
    for i in enrolled_modules:
        for j in modules:
            if(j.get('code')==i):
                enrolled_modules_array.append(j)

    for i in enrolled_modules_array:
        if len(filterEnrollment)>0:
            if(i['rateNumber']>0):
                i['rating']=int(i['rateNumber']*100/len(filterEnrollment))
            else:
                i['rating']=0
        else:
                i['rating']=0
    file1.close()

    return render_template('confirmation.html',enrolled_modules=enrolled_modules_array,id=user.id,email=user.email,name=user.name,stringEnrolled=json.dumps(enrolled_modules_array))



@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password,email=email,name=name,interest=json.dumps(request.form.getlist('mycheckbox')),preference=request.form.getlist('mycheckboxP')[0])
        db.session.add(user)
        db.session.commit()       
        return redirect(url_for('login'))
    UserGet=User.query.all()
    user_arr=[]

    for i in UserGet:
        object_user={
            "username":i.username,
            "email":i.email
        }
        user_arr.append(object_user)
    user_arr=json.dumps(user_arr)
    return render_template('registration.html',user_arr=user_arr)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)


    