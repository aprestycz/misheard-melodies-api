from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database; this creates a file named "lyrics.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lyrics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database object
db = SQLAlchemy(app)

# Define a model for our lyric entries
class Lyric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(500), nullable=False)
    misheard = db.Column(db.String(500), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    song_title = db.Column(db.String(300), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(300), nullable=True)  # Comma-separated tags
    youtube_link = db.Column(db.String(500), nullable=True)
    spotify_link = db.Column(db.String(500), nullable=True)
    amazon_music_link = db.Column(db.String(500), nullable=True)
    embed_youtube = db.Column(db.String(500), nullable=True)  # YouTube Embed Player

    def serialize(self):
        return {
            'id': self.id,
            'original': self.original,
            'misheard': self.misheard,
            'artist': self.artist,
            'song_title': self.song_title,
            'year': self.year,
            'genre': self.genre,
            'tags': self.tags.split(',') if self.tags else [],
            'youtube_link': self.youtube_link,
            'spotify_link': self.spotify_link,
            'amazon_music_link': self.amazon_music_link,
            'embed_youtube': self.embed_youtube
        }


@app.route('/')
def home():
    return "Welcome to the Misheard Lyrics API!"

# GET endpoint to retrieve all lyrics
@app.route('/lyrics', methods=['GET'])
def get_lyrics():
    all_lyrics = Lyric.query.all()
    return jsonify([lyric.serialize() for lyric in all_lyrics])

# POST endpoint to add a new lyric
@app.route('/lyrics', methods=['POST'])
@app.route('/lyrics', methods=['POST'])
def add_lyric():
    data = request.get_json()

    # Check if required fields exist in the request, otherwise return an error
    required_fields = ['original', 'misheard', 'artist', 'song_title']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"'{field}' is required"}), 400  # Bad Request

    # Insert data into the database with optional fields set to None if missing
    new_lyric = Lyric(
        original=data['original'],
        misheard=data['misheard'],
        artist=data['artist'],
        song_title=data['song_title'],
        year=data.get('year', None),  # Defaults to None if missing
        genre=data.get('genre', None),
        tags=data.get('tags', None),
        youtube_link=data.get('youtube_link', None),
        spotify_link=data.get('spotify_link', None),
        amazon_music_link=data.get('amazon_music_link', None),
        embed_youtube=data.get('embed_youtube', None),
    )

    db.session.add(new_lyric)
    db.session.commit()
    return jsonify(new_lyric.serialize()), 201

# PUT endpoint to update an existing lyric
@app.route('/lyrics/<int:lyric_id>', methods=['PUT'])
def update_lyric(lyric_id):
    lyric = Lyric.query.get_or_404(lyric_id)
    data = request.get_json()
    if 'original' in data:
        lyric.original = data['original']
    if 'misheard' in data:
        lyric.misheard = data['misheard']
    db.session.commit()
    return jsonify(lyric.serialize())

# DELETE endpoint to delete an existing lyric
@app.route('/lyrics/<int:lyric_id>', methods=['DELETE'])
def delete_lyric(lyric_id):
    lyric = Lyric.query.get_or_404(lyric_id)
    db.session.delete(lyric)
    db.session.commit()
    return jsonify({'message': 'Lyric deleted'})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Get Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=True)




