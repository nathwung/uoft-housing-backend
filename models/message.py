from models import db

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String, db.ForeignKey('listing.id'), nullable=False)
    from_user = db.Column(db.Boolean, nullable=False)
    sender_name = db.Column(db.String, nullable=True)
    recipient_name = db.Column(db.String, nullable=True)
    text = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'from_user': self.from_user,
            'sender_name': self.sender_name,
            'recipient_name': self.recipient_name,
            'text': self.text
        }

    @staticmethod
    def from_dict(data):
        try:
            return Message(
                listing_id=data['listing_id'],
                from_user=data.get('from_user', True),
                sender_name=data.get('sender_name'),
                recipient_name=data.get('recipient_name'),
                text=data['text']
            )
        except Exception as e:
            raise ValueError(f"Invalid message data: {e}")
