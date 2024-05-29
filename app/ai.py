import joblib
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import numpy as np

ai_bp = Blueprint('ai', __name__)

# Încărcarea modelelor antrenate
price_predict_model = joblib.load('price_predict_rf_optimized.pkl')
recommendation_model = joblib.load('recommendation_model.pkl')


@ai_bp.route('/predict_price', methods=['POST'])
@jwt_required()
def predict_price():
    try:
        data = request.get_json()
        # Preluare caracteristici necesare pentru predicție
        features = np.array([data['features']])
        predicted_price = price_predict_model.predict(features)
        return jsonify({'predicted_price': predicted_price[0]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/recommend_properties', methods=['POST'])
@jwt_required()
def recommend_properties():
    try:
        data = request.get_json()
        # Preluare caracteristici necesare pentru recomandare
        features = np.array([data['features']])
        cluster = recommendation_model.predict(features)
        # Găsește proprietăți care aparțin aceluiași cluster
        properties = find_properties_by_cluster(cluster[0])
        return jsonify({'recommended_properties': properties}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def find_properties_by_cluster(cluster_id):
    # Funcție fictivă care returnează o listă de proprietăți bazată pe cluster
    # Aceasta funcție trebuie să fie implementată pentru a returna proprietățile din baza de date
    return [
        {"id": 1, "name": "Property 1", "cluster": cluster_id},
        {"id": 2, "name": "Property 2", "cluster": cluster_id}
    ]
