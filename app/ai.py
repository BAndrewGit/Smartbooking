import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans

ai_bp = Blueprint('ai', __name__)

# Încărcarea datelor inițiale
df = pd.read_csv('clean_dataset_Romania.csv')

# Codificarea one-hot
df = pd.get_dummies(df, columns=['type', 'address/region', 'rooms/0/roomType'])

# Creează o listă cu numele coloanelor codificate cu one-hot
one_hot_col = [col for col in df.columns if 'type_' in col or 'address/region_' in col or 'rooms/0/roomType_' in col]

# Adaugă coloanele predefinite la listă
selected_columns = one_hot_col + [
    'rooms/0/persons', 'stars', 'Mic dejun', 'Vedere la oraș', 'Menaj zilnic', 'Canale prin satelit',
    'Zonă de luat masa în aer liber', 'Cadă', 'Facilităţi de călcat', 'Izolare fonică', 'terasă la soare',
    'Pardoseală de gresie/marmură', 'Papuci de casă', 'uscător de rufe', 'Animale de companie', 'Încălzire',
    'Birou', 'mobilier exterior', 'Alarmă de fum', 'Vedere la grădină', 'Cuptor', 'Cuptor cu microunde',
    'Zonă de relaxare', 'Canapea', 'Intrare privată', 'Fier de călcat', 'Mașină de cafea', 'Plită de gătit',
    'Extinctoare', 'Cană fierbător', 'grădină', 'Ustensile de bucătărie', 'Maşină de spălat', 'Balcon',
    'Pardoseală de lemn sau parchet', 'Aparat pentru prepararea de ceai/cafea', 'Zonă de luat masa',
    'Canale prin cablu', 'aer condiţionat', 'Masă', 'Suport de haine', 'Cadă sau duş', 'Frigider'
]

# Selectează doar coloanele dorite din DataFrame
features_df = df[selected_columns]
target = df['price']

# Împărțirea datelor în seturi de învățare și testare
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

# Selectarea caracteristicilor și a țintei pentru fiecare set de date
features_train = df_train[features_df.columns]
target_train = df_train['price']

features_test = df_test[features_df.columns]
target_test = df_test['price']

# Crearea imputerului pentru a înlocui valorile lipsă
imputer = SimpleImputer(strategy='mean')

features_train = imputer.fit_transform(features_train)
features_test = imputer.transform(features_test)

# Eliminare Outlieri
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1

df_optimized = df[(df['price'] >= Q1 - 1.5 * IQR) & (df['price'] <= Q3 + 1.5 * IQR)]

# Antrenare model pe datele curățate
features_optimized = df_optimized[selected_columns]
target_optimized = df_optimized['price']

# Împărțirea datelor în seturi de antrenament și testare
features_train_optimized, features_test_optimized, target_train_optimized, target_test_optimized = train_test_split(
    features_optimized, target_optimized, test_size=0.2, random_state=0
)

# Normalizare și scalare
scaler = StandardScaler()
features_train_scaled = scaler.fit_transform(features_train_optimized)
features_test_scaled = scaler.transform(features_test_optimized)

# Crearea modelului RandomForestRegressor
model_rf_optimized = RandomForestRegressor(random_state=0)

# Antrenarea modelului pe datele optimizate
model_rf_optimized.fit(features_train_optimized, target_train_optimized.to_numpy())

# Modelul de recomandare (KMeans)
kmeans = KMeans(n_clusters=5, n_init='auto')
kmeans.fit(df[['price', 'Nota Personal', 'Nota Facilităţi', 'Nota Curăţenie', 'Nota Confort',
               'Nota Raport calitate/preţ', 'Nota Locaţie', 'Nota WiFi gratuit']])
df['cluster'] = kmeans.labels_

@ai_bp.route('/predict_price', methods=['POST'])
@jwt_required()
def predict_price():
    try:
        data = request.get_json()
        input_features = np.array([data['features']])
        input_features = imputer.transform(input_features)  # Imputarea valorilor lipsă
        input_features = scaler.transform(input_features)  # Normalizare și scalare
        predicted_price = model_rf_optimized.predict(input_features)
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
