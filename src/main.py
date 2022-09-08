"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_user():
	users = User.query.all()
	users = list(map(lambda user: user.serialize(),users))
	print(users)
	return jsonify(users), 200

@app.route('/user/<user_id>', methods=['PUT'])
def resgister_user(user_id):
	body = request.json
	user = User.query.get(user_id)
	if not (isinstance(user, User)):
		user = User()

	user.email = body["email"]
	user.password = body["password"]
	user.is_active = body["is_active"]

	db.session.add(user)
	try:        
		db.session.commit()
		return jsonify(user.serialize()), 201
	except Exception as error:
		print(error)
		db.session.rollback()
		return jsonify({"message":error}), 400

@app.route('/planet', methods=['GET'])
def get_planets():
  planets = Planet.query.all()
  planets = list(map(lambda planet: planet.serialize(),planets))
  print(planets)
  return jsonify(planets), 200

@app.route('/planet/<planet_id>', methods=['GET'])
def get_planet(planet_id):
	planet = Planet.query.get(planet_id)
	if isinstance(planet, Planet):
			return jsonify(planet.internal()), 200
	else:
			return jsonify({
					"message":"Planeta no encontrado"
			})

@app.route('/planet', methods=['POST'])
def register_planet():
	"""
	Función con método POST para registrar
	"""
	planet = Planet()
	body = request.json
	
	planet.name = body["name"]
	planet.climate = body["climate"]
	planet.created = body["created"]
	planet.diameter= body["diameter"]
	planet.gravity = body["gravity"]
	planet.orbital_period = body["orbital_period"]

	db.session.add(planet)
	try:        
			db.session.commit()
			return jsonify(planet.serialize()), 201
	except Exception as error:
			print(error)
			db.session.rollback()
			return jsonify({"message":error}), 400

@app.route('/planet/<planet_id>', methods=['PUT'])
def full_update_planet(planet_id):
	body = request.json
	planet = Planet.query.get(planet_id)
	if not (isinstance(planet, Planet)):
		planet = Planet();

	planet.climate = body["climate"]
	planet.created = body["created"]
	planet.diameter= body["diameter"]
	planet.gravity = body["gravity"]
	planet.name = body["name"]
	planet.orbital_period = body["orbital_period"]
	
	db.session.add(planet)
	try:        
		db.session.commit()
		return jsonify(planet.serialize()), 200
	except Exception as error:
		print(error)
		db.session.rollback()
		return jsonify({"message":error}), 400

@app.route('/planet/<planet_id>', methods=['PATCH'])
def partial_update_planet(planet_id):
	body = request.json
	planet = Planet.query.get(planet_id)
	for field in body:
		setattr(planet, field, body[field])
	
	db.session.add(planet)
	try:        
		db.session.commit()
		return jsonify(planet.serialize()), 200
	except Exception as error:
		print(error)
		db.session.rollback()
		return jsonify({"message":error}), 400

@app.route('/planet/<planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
	planet = Planet.query.get(planet_id)
	db.session.delete(planet)
	try:        
		db.session.commit()
		return jsonify( {"message":"Registro eliminado"}), 200
	except Exception as error:
		print(error)
		db.session.rollback()
		return jsonify({"message":error}), 400

@app.route('/people', methods=['GET'])
def get_peoples():
  peoples = People.query.all()
  peoples = list(map(lambda people: people.serialize(),peoples))
  print(peoples)
  return jsonify(peoples), 200

@app.route('/people/<people_id>', methods=['GET'])
def get_people(people_id):
	people = People.query.get(people_id)
	if isinstance(people, People):
			return jsonify(people.internal()), 200
	else:
			return jsonify({
					"message":"Persona no encontrada"
			})

@app.route('/people/<people_id>', methods=['PUT'])
def full_update_people(people_id):
	body = request.json
	people = People.query.get(people_id)
	if not (isinstance(people, People)):
		people = People();

	people.name = body["name"]
	people.gender = body["gender"]
	people.birth_year= body["birth_year"]
	
	db.session.add(people)
	try:        
		db.session.commit()
		return jsonify(people.serialize()), 200
	except Exception as error:
		print(error)
		db.session.rollback()
		return jsonify({"message":error}), 400



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
