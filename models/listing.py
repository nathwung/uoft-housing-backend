from models import db

class Listing(db.Model):
    __tablename__ = 'listing'

    id = db.Column(db.String, primary_key=True)  # UUID string
    title = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    price = db.Column(db.Float)
    negotiable = db.Column(db.Boolean)
    description = db.Column(db.String)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    furnished = db.Column(db.Boolean)
    amenities = db.Column(db.String)  # comma-separated string
    images = db.Column(db.PickleType)  # list of image URLs/base64
    startDate = db.Column(db.String)
    endDate = db.Column(db.String)
    roommatePreference = db.Column(db.String)

    poster_name = db.Column(db.String)
    poster_email = db.Column(db.String)
    poster_program = db.Column(db.String)
    poster_year = db.Column(db.String)
    poster_avatar = db.Column(db.String)

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    messages = db.relationship('Message', backref='listing', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'location': self.location,
            'price': self.price,
            'negotiable': self.negotiable,
            'description': self.description,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'furnished': self.furnished,
            'amenities': self.amenities.split(',') if self.amenities else [],
            'images': self.images,
            'startDate': self.startDate,
            'endDate': self.endDate,
            'roommatePreference': self.roommatePreference,
            'poster': {
                'name': self.poster_name,
                'email': self.poster_email,
                'program': self.poster_program,
                'year': self.poster_year,
                'avatar': self.poster_avatar
            },
            'lat': self.lat,
            'lng': self.lng
        }
