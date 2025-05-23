from flask import Blueprint, request, jsonify
from models import db
from models.listing import Listing
import uuid

listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/api/listings', methods=['GET'])
def get_all_listings():
    listings = Listing.query.all()
    return jsonify([l.to_dict() for l in listings])

@listings_bp.route('/api/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    return jsonify(listing.to_dict())

@listings_bp.route('/api/listings', methods=['POST'])
def create_listing():
    data = request.get_json()
    listing = Listing(
        id=str(uuid.uuid4()),
        title=data.get('title'),
        type=data.get('type'),
        location=data.get('location'),
        price=data.get('price'),
        negotiable=data.get('negotiable'),
        description=data.get('description'),
        bedrooms=data.get('bedrooms'),
        bathrooms=data.get('bathrooms'),
        furnished=data.get('furnished'),
        amenities=','.join(data.get('amenities', [])),
        images=data.get('images', []),
        startDate=data.get('startDate'),
        endDate=data.get('endDate'),
        roommatePreference=data.get('roommatePreference'),
        lat=data.get('lat'), 
        lng=data.get('lng'),  
        poster_name=data['poster']['name'],
        poster_email=data['poster']['email'],
        poster_program=data['poster']['program'],
        poster_year=data['poster']['year'],
        poster_avatar=data['poster']['avatar']
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify(listing.to_dict()), 201

@listings_bp.route('/api/listings/<listing_id>', methods=['PUT'])
def update_listing(listing_id):
    data = request.get_json()
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    for field in ['title', 'type', 'location', 'price', 'negotiable', 'description',
                  'bedrooms', 'bathrooms', 'furnished', 'startDate', 'endDate',
                  'roommatePreference', 'images']:
        if field in data:
            setattr(listing, field, data[field])
    if 'amenities' in data:
        listing.amenities = ','.join(data['amenities'])
    if 'poster' in data:
        listing.poster_name = data['poster'].get('name')
        listing.poster_email = data['poster'].get('email')
        listing.poster_program = data['poster'].get('program')
        listing.poster_year = data['poster'].get('year')
        listing.poster_avatar = data['poster'].get('avatar')

    db.session.commit()
    return jsonify(listing.to_dict())

@listings_bp.route('/api/listings/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    db.session.delete(listing)
    db.session.commit()
    return jsonify({'message': 'Listing deleted'})

def update_poster_info_internal(user_data):
    email = user_data.get('email')
    listings = Listing.query.filter_by(poster_email=email).all()
    for l in listings:
        l.poster_name = user_data.get('name', l.poster_name)
        l.poster_program = user_data.get('program', l.poster_program)
        l.poster_year = user_data.get('year', l.poster_year)
        l.poster_avatar = user_data.get('avatar', l.poster_avatar)
    db.session.commit()
