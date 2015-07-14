from WIAPI import db
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Enum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import datetime
import base64
from werkzeug.security import generate_password_hash, check_password_hash

class Offer(db.Model):
	__tablename__ = 'offers'
	id = Column(Integer, primary_key=True)
	title = Column(String)
	description = Column(String)
	venue = Column(String)
	start_time = Column(DateTime)
	end_time = Column(DateTime)
	created_at = Column(DateTime)
	users = association_proxy('user_offers', 'user', creator=lambda u: UserOfferResponse(user=u))

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

	def json_for_user(self, user):
		json = self.toJSON()
		response = UserOfferResponse.find_by_offer_and_user(self, user)
		json['response'] = response.response if response else None
		return json

class User(db.Model):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	first_name = Column(String, nullable=False)
	last_name = Column(String, nullable=False)
	email = Column(String, index=True, unique=True)
	facebook_id = Column(String)
	hash = Column(String)
	type = Column(Enum('Customer', 'Staff', name='user_types'), default='Customer')
	created_at = Column(DateTime)
	offers = association_proxy('offer_users', 'offer', creator=lambda o: UserOfferResponse(offer=o))

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

class UserOfferResponse(db.Model):
	__tablename__ = 'user_offer_responses'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	offer_id = Column(Integer, ForeignKey('offers.id'))
	response = Column(String)
	created_at = Column(DateTime)

	offer = relationship(Offer, backref=backref("user_offers", cascade="all, delete-orphan"))
	user = relationship(User, backref=backref("offer_users", cascade="all, delete-orphan"))

	def __init__(self, offer=None, user=None, response="", created_at=datetime.datetime.now()):
		self.response = response
		self.offer = offer
		self.user = user
		self.created_at = created_at

	def __repr__(self):
		return '<UserOfferResponse {}: {}<->{}: {}>'.format(self.id, self.offer.id, self.user.email, self.response)

	def toJSON(self):
		return {'response': self.response}

	@staticmethod
	def find_by_offer_and_user(offer, user):
		return UserOfferResponse.query.filter(UserOfferResponse.user_id == user.id)\
												.filter(UserOfferResponse.offer_id == offer.id).first()

class ValidResponses(object):
	ACCEPT = "ACCEPT"
	DECLINE = "DECLINE"
	BLOCK_VENUE = "BLOCK_VENUE"
	TIMEOUT_VENUE = "TIMEOUT_VENUE"
	FLAG_INAPPROPRIATE = "INAPPROPRIATE"
