from WIAPI import db
from sqlalchemy.dialects.postgresql import JSON

class Offer(db.Model):
	__tablename__ = 'offers'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	description = db.Column(db.String)
	venue = db.Column(db.String)

	def __init__(self, title, description, venue):
		self.title = title
		self.description = description
		self.venue = venue

	def __repr__(self):
		return '<Offer {}: {}>'.format(self.id, self.title)

	def toJSON(self):
		whitelist = ['id', 'title', 'venue', 'description']
		return {attr: getattr(self, attr) for attr in whitelist}
