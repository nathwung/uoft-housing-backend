from flask import Blueprint, jsonify, request
from models.message import Message
from models.listing import Listing
from models import db
from datetime import datetime, timezone

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/api/messages/<listing_id>', methods=['GET'])
def get_messages(listing_id):
    sender_name = request.args.get('sender_name')

    query = Message.query.filter_by(listing_id=listing_id)

    if sender_name:
        query = query.filter_by(sender_name=sender_name)

    messages = query.all()
    return jsonify([m.to_dict() for m in messages])

@messages_bp.route('/api/messages/<listing_id>', methods=['POST'])
def post_message(listing_id):
    data = request.json
    print('Incoming message payload:', data)

    if not data or 'text' not in data or 'sender_name' not in data:
        return jsonify({'error': 'Invalid message data'}), 400

    try:
        data['listing_id'] = listing_id  # Inject listing ID before conversion
        message = Message.from_dict(data)
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201
    except Exception as e:
        print("Error creating message:", e)
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/api/messages/<listing_id>/<int:message_id>', methods=['DELETE'])
def delete_message(listing_id, message_id):
    message = Message.query.filter_by(id=message_id, listing_id=listing_id).first()
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()
    return jsonify({'success': True})

@messages_bp.route('/api/messages/grouped/<listing_id>', methods=['GET'])
def get_grouped_messages(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    poster_name = listing.poster_name
    all_messages = Message.query.filter_by(listing_id=listing_id).all()
    grouped = {}

    for msg in all_messages:
        if msg.sender_name != poster_name:
            key = msg.sender_name
        else:
            key = msg.recipient_name

        if not key:
            continue

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(msg.to_dict())

    return jsonify(grouped)

def update_sender_name_internal(old_name, new_name):
    messages = Message.query.filter_by(sender_name=old_name).all()
    for m in messages:
        m.sender_name = new_name
    db.session.commit()
