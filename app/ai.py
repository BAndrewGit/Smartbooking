import joblib
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import numpy as np
import pandas as pd

ai_bp = Blueprint('ai', __name__)

# Încărcarea modelelor antrenate
price_predict_model = joblib.load('price_predict_rf_optimized.pkl')
recommendation_model = joblib.load('recommendation_model.pkl')

# Încărcarea datelor inițiale (exemplu, puteți înlocui cu datele reale)
df = pd.read_csv('clean_dataset_Romania.csv')


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
        user_ratings = data['user_ratings']
        preferred_accommodations = data['preferred_accommodations']
        max_budget = data['max_budget']
        preferred_region = data['preferred_region']

        # Calculăm scorul de preferință pentru fiecare hotel
        for index, row in df.iterrows():
            preference_score = 0
            for category, user_rating in user_ratings.items():
                preference_score += row[category] * user_rating
            df.loc[index, 'preference_score'] = preference_score

        # Adăugăm etichetele de cluster la DataFrame
        df['cluster'] = recommendation_model.predict(df[['price', 'Nota Personal', 'Nota Facilităţi', 'Nota Curăţenie',
                                                         'Nota Confort', 'Nota Raport calitate/preţ', 'Nota Locaţie',
                                                         'Nota WiFi gratuit']])

        # Identificăm clusterul preferat
        preferred_cluster = df[df['name'].isin(preferred_accommodations)]['cluster'].mode()[0]

        # Filtrăm DataFrame-ul pentru a include doar hotelurile din clusterul preferat
        df_filtered = df[df['cluster'] == preferred_cluster]

        # Aplicăm filtrele
        df_filtered = df_filtered[df_filtered['price'] <= max_budget]
        df_filtered = df_filtered[df_filtered['address/region'] == preferred_region]

        # Identificăm facilitățile care sunt disponibile la cazări preferate
        preferred_facilities = df[df['name'].isin(preferred_accommodations)].iloc[:, -37:].sum(axis=0)

        # Calculăm scorul de potrivire a facilităților pentru fiecare hotel
        for index, row in df_filtered.iterrows():
            matching_facilities_score = sum(row[-37:] * preferred_facilities)
            df_filtered.loc[index, 'preference_score'] += matching_facilities_score

        # Afișăm primele 5 hoteluri cu cel mai mare scor de preferință
        recommendations = df_filtered.nlargest(5, 'preference_score')

        return jsonify(recommendations.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def find_properties_by_cluster(cluster_id):
    # Funcție fictivă care returnează o listă de proprietăți bazată pe cluster
    # Aceasta funcție trebuie să fie implementată pentru a returna proprietățile din baza de date
    properties = df[df['cluster'] == cluster_id]
    return properties.to_dict(orient='records')
