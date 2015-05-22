import json
from flask import request, abort
from flask.ext.restful import reqparse, Resource
from WIAPI import app, api, mongo
from bson.objectid import ObjectId

class Offer(Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True, help="Title is required")
        self.parser.add_argument('description', type=str, required=True, help="Description is required")
        self.parser.add_argument('venue', type=str, required=True, help="Venue is required")
        super(Offer, self).__init__()

    def post(self):
        args = self.parser.parse_args()
        offer = {
            'title': args['title'],
            'description': args['description'],
            'venue': args['description']
        }

        offer_id =  mongo.db.offers.insert(offer)
        return mongo.db.offers.find_one({"_id": offer_id})

    def delete(self, offer_id):
        mongo.db.offers.find_one_or_404({"_id": offer_id})
        mongo.db.offers.remove({"_id": offer_id})
        return '', 204

def export_offer(offer):
    offer['id'] = str(offer['_id'])
    return offer

class MyOffersList(Resource):
    def get(self):
        return  [export_offer(x) for x in mongo.db.offers.find()]

class NearbyOffersList(Resource):
    def get(self):
        return  [export_offer(x) for x in mongo.db.offers.find()]

class Root(Resource):
    def get(self):
        return {
            'status': 'OK',
            'mongo': str(mongo.db),
            'message': "I'm fine"
        }

api.add_resource(Root, '/')
api.add_resource(MyOffersList, '/offers/mine')
api.add_resource(NearbyOffersList, '/offers/nearby')
api.add_resource(Offer, '/offers/<ObjectId:offer_id>', '/offers')
