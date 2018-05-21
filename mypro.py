from flask import Flask,render_template,session,redirect,url_for,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail,Message

from datetime import datetime
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['MAIL_SERVER'] = 'smtp.sina.cn'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'sjc_111111@sina.cn'#os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = '11ba0shen2'#os.environ.get('MAIL_PASSWORD')
app.config['FLASK_MAIL_PREFIX'] = 'sjc'
app.config['FLASKY_MAIL_SENDER'] = 'sjc_111111@sina.cn'
app.config['FLASK_ADMIN'] = '446474326@qq.com'#os.environ.get('FLASK_ADMIN')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app,db)
mail = Mail(app)

def send_mail(to,subject,template,**kwargs):
    msg = Message(app.config['FLASK_MAIL_PREFIX']+subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    mail.send(msg)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User',backref = 'role')
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' % self.username

class NameForm(Form):
    name = StringField("what's you name ?",validators=[Required()])
    submit = SubmitField('submit')

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('db',MigrateCommand)

@app.route('/',methods = ['GET','POST'])
def hello_world():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASK_ADMIN']:
                send_mail(app.config['FLASK_ADMIN'],
                          'New User',
                          'mail/new_user',
                          user=user)
        else:
            session['known'] = True
        oldname = session.get('name')
        if oldname is not None and oldname != form.name.data:
            flash('change name')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('hello_world'))
    return  render_template('base.html',
                            form=form,
                            name=session.get('name'),
                            known=session.get('known',False))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route('/user/<name>')
def hello(name):
    return render_template('user.html',name=name)

if __name__ == '__main__':
    app.run()
