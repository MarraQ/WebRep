from flask import jsonify
from flask_restful import Resource, reqparse, abort

from data import db_session
from data.ads import Ad

parser = reqparse.RequestParser()
parser.add_argument("title", required=True)
parser.add_argument("description", required=True)
parser.add_argument("price", required=True, type=int)
parser.add_argument("owner_id", required=True, type=int)


def abort_if_ads_not_found(ad_id):
    session = db_session.create_session()
    ads = session.query(Ad).get(ad_id)
    if not ads:
        abort(404, message=f"Ad {ad_id} not found")


class AdsResource(Resource):
    def get(self, ad_id):
        abort_if_ads_not_found(ad_id)
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).get(ad_id)
        return jsonify({'ad': {"title": ad.title, "description": ad.description, "price": ad.price}})

    def delete(self, ad_id):
        abort_if_ads_not_found(ad_id)
        session = db_session.create_session()
        ad = session.query(Ad).get(ad_id)
        session.delete(ad)
        session.commit()
        return jsonify({'success': 'OK'})


class AdsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        ads = db_sess.query(Ad).all()
        return jsonify({"ads": [
            {
                "title": item.title,
                "description": item.description,
                "user.name": item.user.nickname
            } for item in ads]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        ads = Ad(
            title=args["title"],
            description=args["description"],
            owner_id=args["owner_id"],
            price=args["price"]
        )
        db_sess.add(ads)
        db_sess.commit()
        return jsonify({'id': ads.id})
