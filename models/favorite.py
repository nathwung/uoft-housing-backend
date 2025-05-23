from app import db

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String, nullable=False)
    listing_id = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "listing_id": self.listing_id
        }
