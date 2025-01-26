from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Enable CORS to allow communication between React and Flask
CORS(app)

# Setup database migration
migrate = Migrate(app, db)

# Initialize the database
db.init_app(app)

# Route to handle all messages
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Fetch all messages ordered by creation time
        messages = Message.query.order_by('created_at').all()

        return make_response(
            jsonify([message.to_dict() for message in messages]),
            200,
        )

    elif request.method == 'POST':
        data = request.get_json()

        # Create a new message record
        message = Message(
            body=data.get('body'),
            username=data.get('username')
        )

        db.session.add(message)
        db.session.commit()

        return make_response(
            jsonify(message.to_dict()),
            201,
        )

# Route to handle operations on individual messages
@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    if request.method == 'PATCH':
        data = request.get_json()

        # Update message fields
        for attr, value in data.items():
            if hasattr(message, attr):
                setattr(message, attr, value)

        db.session.commit()

        return make_response(
            jsonify(message.to_dict()),
            200,
        )

    elif request.method == 'DELETE':
        # Delete the message
        db.session.delete(message)
        db.session.commit()

        return make_response(
            jsonify({"deleted": True}),
            200,
        )

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5555)