from WIAPI import db
from sqlalchemy.dialects.postgresql import JSON
import datetime
import base64
from werkzeug.security import generate_password_hash, check_password_hash

class Offer(db.Model):
	__tablename__ = 'offers'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	description = db.Column(db.String)
	venue = db.Column(db.String)
	start_time = db.Column(db.DateTime)
	end_time = db.Column(db.DateTime)
	created_at = db.Column(db.DateTime)

	def __init__(self, title, description, venue, start_time, end_time):
		self.title = title
		self.description = description
		self.venue = venue
		self.start_time = start_time
		self.end_time = end_time
		self.created_at = datetime.datetime.utcnow()

	def __repr__(self):
		return '<Offer {}: {}>'.format(self.id, self.title)

	def toJSON(self):
		whitelist = ['id', 'title', 'venue', 'description', 'start_time', 'end_time']
		return {attr: getattr(self, attr) for attr in whitelist}

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, index=True, unique=True)
	facebook_id = db.Column(db.String)
	hash = db.Column(db.String)
	type = db.Column(db.Enum('Customer', 'Staff', name='user_types'), default='Customer')
	created_at = db.Column(db.DateTime)

	def __init__(self, first_name, last_name, email, password, facebook_id=None, type='Customer'):
		self.first_name = first_name
		self.last_name = last_name
		self.email = email.lower()
		self.hash = generate_password_hash(password)
		self.facebook_id = facebook_id
		self.type = type
		self.created_at = datetime.datetime.utcnow()

	def __repr__(self):
		return '<User {}: {}>'.format(self.id, self.email)

	def check_password(self, password):
		return check_password_hash(self.hash, password)

	@staticmethod
	def find_by_email(email):
		return User.query.filter_by(email=email).first()

	@staticmethod
	def find_by_auth_token(token):
		id, hash = token.split(":&&:")
		return User.query.filter_by(id=id, hash=hash).first()

	def is_authenticated(self):
		return bool(self.email)

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)

	def get_auth_token(self):
		return base64.b64encode("{}:&&:{}".format(self.id, self.hash))	

	def toJSON(self):
		whitelist = ['id', 'first_name', 'last_name', 'email', 'type']
		user = {attr: getattr(self, attr) for attr in whitelist}
		user.update({
			'auth_token': self.get_auth_token()
		})
		return user
