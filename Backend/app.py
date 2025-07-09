import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv()

app = Flask(__name__, instance_relative_config=True)

# Load config from config.py (project root or instance/)
app.config.from_pyfile(os.getenv('FLASK_CONFIG', 'config.py'), silent=True)

# Override with environment variables (recommended for secrets)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', app.config.get('SQLALCHEMY_DATABASE_URI'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# --- Models ---
class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    container_number = db.Column(db.String(20), nullable=False)
    iso_code = db.Column(db.String(10))
    other_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

# --- Routes ---
with app.app_context():
    db.create_all()

# CREATE - Ajouter un nouveau conteneur (EXISTANT)
@app.route('/api/containers', methods=['POST'])
def add_container():
    data = request.get_json()
    container_number = data.get('container_number')
    iso_code = data.get('iso_code')
    other_info = data.get('other_info')

    if not container_number:
        return jsonify({'error': 'container_number is required'}), 400

    # Vérifier si le conteneur existe déjà
    existing_container = Container.query.filter_by(container_number=container_number).first()
    if existing_container:
        return jsonify({'error': 'Container with this number already exists'}), 409

    new_container = Container(
        container_number=container_number,
        iso_code=iso_code,
        other_info=other_info
    )
    db.session.add(new_container)
    db.session.commit()
    return jsonify({'message': 'Container saved', 'id': new_container.id}), 201

# READ - Récupérer tous les conteneurs (EXISTANT)
@app.route('/api/containers', methods=['GET'])
def get_containers():
    containers = Container.query.all()
    results = []
    for c in containers:
        results.append({
            'id': c.id,
            'container_number': c.container_number,
            'iso_code': c.iso_code,
            'other_info': c.other_info,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None
        })
    return jsonify(results)

# READ - Récupérer un conteneur spécifique par ID (NOUVEAU)
@app.route('/api/containers/<int:container_id>', methods=['GET'])
def get_container(container_id):
    container = Container.query.get(container_id)
    if not container:
        return jsonify({'error': 'Container not found'}), 404
    
    return jsonify({
        'id': container.id,
        'container_number': container.container_number,
        'iso_code': container.iso_code,
        'other_info': container.other_info,
        'created_at': container.created_at.isoformat() if container.created_at else None,
        'updated_at': container.updated_at.isoformat() if container.updated_at else None
    }), 200

# UPDATE - Modifier un conteneur existant (NOUVEAU)
@app.route('/api/containers/<int:container_id>', methods=['PUT'])
def update_container(container_id):
    container = Container.query.get(container_id)
    if not container:
        return jsonify({'error': 'Container not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Vérifier si le nouveau numéro de conteneur existe déjà (sauf pour ce conteneur)
    if 'container_number' in data:
        existing_container = Container.query.filter(
            Container.container_number == data['container_number'],
            Container.id != container_id
        ).first()
        if existing_container:
            return jsonify({'error': 'Container with this number already exists'}), 409
    
    # Mettre à jour les champs
    if 'container_number' in data:
        container.container_number = data['container_number']
    if 'iso_code' in data:
        container.iso_code = data['iso_code']
    if 'other_info' in data:
        container.other_info = data['other_info']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Container updated successfully',
            'id': container.id,
            'container_number': container.container_number,
            'iso_code': container.iso_code,
            'other_info': container.other_info,
            'created_at': container.created_at.isoformat() if container.created_at else None,
            'updated_at': container.updated_at.isoformat() if container.updated_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update container'}), 500

# DELETE - Supprimer un conteneur (NOUVEAU)
@app.route('/api/containers/<int:container_id>', methods=['DELETE'])
def delete_container(container_id):
    container = Container.query.get(container_id)
    if not container:
        return jsonify({'error': 'Container not found'}), 404
    
    try:
        db.session.delete(container)
        db.session.commit()
        return jsonify({
            'message': 'Container deleted successfully',
            'deleted_container': {
                'id': container.id,
                'container_number': container.container_number
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete container'}), 500

# SEARCH - Rechercher des conteneurs (NOUVEAU)
@app.route('/api/containers/search', methods=['GET'])
def search_containers():
    container_number = request.args.get('number')
    iso_code = request.args.get('iso_code')
    
    if not container_number and not iso_code:
        return jsonify({'error': 'Please provide number or iso_code parameter'}), 400
    
    query = Container.query
    
    if container_number:
        query = query.filter(Container.container_number.ilike(f'%{container_number}%'))
    
    if iso_code:
        query = query.filter(Container.iso_code.ilike(f'%{iso_code}%'))
    
    containers = query.all()
    
    results = []
    for c in containers:
        results.append({
            'id': c.id,
            'container_number': c.container_number,
            'iso_code': c.iso_code,
            'other_info': c.other_info,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None
        })
    
    return jsonify({
        'containers': results,
        'count': len(results)
    }), 200

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
