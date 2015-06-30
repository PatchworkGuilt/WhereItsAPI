import json
from flask import request, abort, render_template, flash, url_for, redirect
from flask.ext.restful import reqparse, Resource
from flask.ext.login import LoginManager, login_required, UserMixin, login_user, logout_user
from WIAPI import app, api, db
from WIAPI import models
import base64
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class OfferEndpoint(Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True, help="Title is required")
        self.parser.add_argument('description', type=str, required=False, help="Description is required")
        self.parser.add_argument('venue', type=str, required=True, help="Venue is required")
        self.parser.add_argument('start_time', type=datetime, required=False, help="StartTime is required", default=datetime.now())
        self.parser.add_argument('end_time', type=datetime, required=False, help="EndTime is required", default=datetime.now())
        super(OfferEndpoint, self).__init__()

    @login_required
    def post(self):
        args = self.parser.parse_args()
        offer = models.Offer(
            title = args['title'],
            description= args['description'],
            venue = args['venue'],
            start_time = args['start_time'],
            end_time = args['end_time']
        )

        db.session.add(offer)
        db.session.commit()
        return '', 200

    @login_required
    def delete(self, offer_id):
        #mongo.db.offers.find_one_or_404({"_id": offer_id})
        #mongo.db.offers.remove({"_id": offer_id})
        return '', 204

    def get(self, offer_id):
        offer = models.Offer.query.get(offer_id)
        return offer.toJSON()

class MyOffersList(Resource):
    @login_required
    def get(self):
        offers = models.Offer.query.all()
        return [offer.toJSON() for offer in offers]

class NearbyOffersList(Resource):
    def get(self):
        offers = models.Offer.query.all()
        return [offer.toJSON() for offer in offers]

class Root(Resource):
    def get(self):
        return {
            'status': 'OK',
            'message': "I'm fine"
        }

class UserEndpoint(Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first_name', type=str, required=True, help="First Name is required")
        self.parser.add_argument('last_name', type=str, required=True, help="Last Name is required")
        self.parser.add_argument('email', type=str, required=True, help="Email is required")
        self.parser.add_argument('password', type=str, required=True, help="Password is required")
    
    def post(self):
        args = self.parser.parse_args()
        user = models.User(
            first_name = args['first_name'], 
            last_name = args['last_name'], 
            email = args['email'], 
            password = args['password']
        )

        db.session.add(user)
        db.session.commit()
        login_user(user)
        return json.dumps(user.toJSON()), 200

api.add_resource(Root, '/')
api.add_resource(MyOffersList, '/offers/mine')
api.add_resource(NearbyOffersList, '/offers/nearby')
api.add_resource(OfferEndpoint, '/offers/<offer_id>', '/offers')
api.add_resource(UserEndpoint, '/users')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return models.User.query.get(userid)

@login_manager.request_loader
def load_user_from_request(request):
    auth_key = request.headers.get('Authorization')
    if auth_key:
        try:
            auth_key = base64.b64decode(auth_key)
            return models.User.find_by_auth_token(auth_key)
        except TypeError:
            return None
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        post = request.get_json()
        email = post.get('email')
        password = post.get('password')
        user = models.User.find_by_email(email)
        if user and user.check_password(password):
            login_user(user, remember=True)
            return json.dumps(user.toJSON()), 200
        return 'Email and password are not correct', 401
    return '', 401

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return '', 200
