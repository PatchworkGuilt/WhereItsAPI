import json
from flask import request, abort
from flask.ext.restful import reqparse, Resource
from WIAPI import app, api, db
from WIAPI.models import Offer
from sqlalchemy.dialects.postgresql import JSON

class OfferEndpoint(Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True, help="Title is required")
        self.parser.add_argument('description', type=str, required=False, help="Description is required")
        self.parser.add_argument('venue', type=str, required=True, help="Venue is required")
        super(OfferEndpoint, self).__init__()

    def get(self):
        args = self.parser.parse_args()
        offer = Offer(
            title = args['title'],
            description= args['description'],
            venue = args['venue']
        )

        db.session.add(offer)
        db.session.commit()
        return '', 200

    def delete(self, offer_id):
        #mongo.db.offers.find_one_or_404({"_id": offer_id})
        #mongo.db.offers.remove({"_id": offer_id})
        return '', 204

class MyOffersList(Resource):
    def get(self):
        offers = Offer.query.all()
        return [offer.toJSON() for offer in offers]

class NearbyOffersList(Resource):
    def get(self):
        offers = Offer.query.all()
        return [offer.toJSON() for offer in offers]

class Root(Resource):
    def get(self):
        return {
            'status': 'OK',
            'message': "I'm fine"
        }

api.add_resource(Root, '/')
api.add_resource(MyOffersList, '/offers/mine')
api.add_resource(NearbyOffersList, '/offers/nearby')
api.add_resource(OfferEndpoint, '/offers/<offer_id>', '/offers')
