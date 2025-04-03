#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class ScientistResource(Resource):
    
    def get(self):
        scientist_dicts = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]

        return scientist_dicts, 200


    def post(self):
        json = request.get_json()
        try:
            new_scientist = Scientist(name=json['name'], field_of_study=json['field_of_study'])
            db.session.add(new_scientist)
            db.session.commit()

            return new_scientist.to_dict(), 201

        except:
            return {"errors": ["validation errors"]} , 400


class ScientistByID(Resource):

    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return scientist.to_dict(), 200
        
        return {"error":"Scientist not found"}, 404


    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:
                json = request.get_json()
                for attr, value in json.items():
                    setattr(scientist, attr, value)

                db.session.add(scientist)
                db.session.commit()

                return scientist.to_dict(), 202

            except:
                return {"errors": ["validation errors"]}, 400
        
        return {"error": "Scientist not found"}, 404

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()

            return "", 204

        return {"error": "Scientist not found"}, 404


class PlanetResource(Resource):

    def get(self):
        planet_dicts = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
        return planet_dicts, 200


class MissionResource(Resource):

    def post(self):
        try:
            json = request.get_json()
            new_mission = Mission(
                name=json['name'],
                scientist_id=json['scientist_id'],
                planet_id=json['planet_id'],
            )
            db.session.add(new_mission)
            db.session.commit()

            return new_mission.to_dict(), 201

        except:
            return {"errors":["validation errors"]}, 400



api.add_resource(ScientistResource, '/scientists')
api.add_resource(ScientistByID, '/scientists/<int:id>')
api.add_resource(PlanetResource, '/planets')
api.add_resource(MissionResource, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
