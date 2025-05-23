from flask import Blueprint, request, jsonify
from models.favorite import Favorite
from models import db

favorites_bp = Blueprint('favorites', __name__)

# GET all favorites for a user
@favorites_bp.route('/api/favorites/<email>', methods=['GET'])
def get_favorites(email):
    favorites = Favorite.query.filter_by(user_email=email).all()
    return jsonify([f.listing_id for f in favorites])

# POST new favorite
@favorites_bp.route('/api/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()
    user_email = data.get('user_email')
    listing_id = data.get('listing_id')
    
    if not user_email or not listing_id:
        return jsonify({'error': 'Missing fields'}), 400

    # Prevent duplicates
    existing = Favorite.query.filter_by(user_email=user_email, listing_id=listing_id).first()
    if existing:
        return jsonify({'message': 'Already favorited'}), 200

    new_fav = Favorite(user_email=user_email, listing_id=listing_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({'message': 'Favorite added'}), 201

# DELETE favorite
@favorites_bp.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    data = request.get_json()
    user_email = data.get('user_email')
    listing_id = data.get('listing_id')

    fav = Favorite.query.filter_by(user_email=user_email, listing_id=listing_id).first()
    if not fav:
        return jsonify({'error': 'Favorite not found'}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': 'Favorite removed'}), 200
