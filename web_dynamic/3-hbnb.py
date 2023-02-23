#!/usr/bin/python3
""" Starts a Flash Web Application """
import uuid

from flask import Flask, render_template
from flask import jsonify, abort, request
from models import storage
from api.v1.views import app_views
from models.city import City
from models.place import Place
from models.user import User
from models.state import State
from models.amenity import Amenity
from flasgger.utils import swag_from

app = Flask(__name__)


# app.jinja_env.trim_blocks = True
# app.jinja_env.lstrip_blocks = True


@app_views.teardown_appcontext
def close_db(error):
    """ Remove the current SQLAlchemy Session """
    storage.close()


@app.route('/3-hbnb/', strict_slashes=False)
def hbnb():
    """ HBNB is alive! """
    states = storage.all(State).values()
    states = sorted(states, key=lambda k: k.name)
    st_ct = []

    for state in states:
        st_ct.append([state, sorted(state.cities, key=lambda k: k.name)])

    amenities = storage.all(Amenity).values()
    amenities = sorted(amenities, key=lambda k: k.name)

    places = storage.all(Place).values()
    places = sorted(places, key=lambda k: k.name)

    return render_template(
        '3-hbnb.html', states=st_ct, amenities=amenities, places=places,
        cache_id=uuid.uuid4())


@app_views.route(
    "/cities/<city_id>/places", methods=["GET"], strict_slashes=False)
def place_by_city(city_id):
    """View function that return place objects by city"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route("/places/<place_id>", methods=["GET"], strict_slashes=False)
def show_place(place_id):
    """Endpoint that return a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route("/places/<place_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_place(place_id):
    """Endpoint that delete a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({})


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def insert_place(city_id):
    """Endpoint that insert a Place object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    res = request.get_json()
    if type(res) != dict:
        abort(400, description="Not a JSON")
    if not res.get("user_id"):
        abort(400, description="Missing user_id")
    user = storage.get(User, res.get("user_id"))
    if user is None:
        abort(404)
    if not res.get("name"):
        abort(400, description="Missing name")
    new_place = Place(**res)
    new_place.city_id = city_id
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
def places_search():
    """Retrieves all Place objects depending on the body of the request"""
    body = request.get_json()
    if type(body) != dict:
        abort(400, description="Not a JSON")
    id_states = body.get("states", [])
    id_cities = body.get("cities", [])
    id_amenities = body.get("amenities", [])

    if id_states == id_cities == []:
        places = storage.all(Place).values()
    else:
        states = [storage.get(State, _id) for _id in id_states if storage.get(
            State, _id)]
        cities = [city for state in states for city in state.cities]
        cities.extend([
            storage.get(City, _id) for _id in id_cities
            if storage.get(City, _id)
        ])
        cities = list(set(cities))
        places = [place for city in cities for place in city.places]

    amenities = [
        storage.get(Amenity, _id) for _id in id_amenities
        if storage.get(Amenity, _id)
    ]

    results = []
    for place in places:
        results.append(place.to_dict())
        for amenity in amenities:
            if amenity not in place.amenities:
                results.pop()
                break

    return jsonify(results)


@app_views.route("/places/<place_id>", methods=["PUT"], strict_slashes=False)
def update_place(place_id):
    """update a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    props = request.get_json()
    if type(props) != dict:
        abort(400, description="Not a JSON")
    for k, v in props.items():
        if k not in ["id", "user_id", "city_id", "created_at", "updated_at"]:
            setattr(place, k, v)
    storage.save()
    return jsonify(place.to_dict()), 200


if __name__ == "__main__":
    """ Main Function """
    app.run(host='0.0.0.0', port=5000)
