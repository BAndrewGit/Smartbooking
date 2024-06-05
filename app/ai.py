import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from .models import Favorite, Property, Room, Review, UserPreferences, db, Reservation

# Încărcarea datelor inițiale
df = pd.read_csv('clean_dataset_Romania.csv')

# Codificarea one-hot
df = pd.get_dummies(df, columns=['type', 'region', 'room_type'])

# Creează o listă cu numele coloanelor codificate cu one-hot
one_hot_columns = [col for col in df.columns if 'type_' in col or 'region_' in col or 'room_type_' in col]

# Adaugă coloanele predefinite la listă
selected_columns = one_hot_columns + [
    'persons', 'stars', 'mic_dejun', 'nota_personal', 'nota_facilităţi', 'nota_curăţenie',
    'nota_confort', 'nota_raport_calitate/preţ', 'nota_locaţie', 'nota_wifi_gratuit', 'num_reviews',
    'vedere_la_oraș', 'menaj_zilnic', 'canale_prin_satelit', 'zonă_de_luat_masa_în_aer_liber', 'cadă',
    'facilităţi_de_călcat', 'izolare_fonică', 'terasă_la_soare', 'pardoseală_de_gresie/marmură',
    'papuci_de_casă', 'uscător_de_rufe', 'animale_de_companie', 'încălzire', 'birou', 'mobilier_exterior',
    'alarmă_de_fum', 'vedere_la_grădină', 'cuptor', 'cuptor_cu_microunde', 'zonă_de_relaxare', 'canapea',
    'intrare_privată', 'fier_de_călcat', 'mașină_de_cafea', 'plită_de_gătit', 'extinctoare', 'cană_fierbător',
    'grădină', 'ustensile_de_bucătărie', 'maşină_de_spălat', 'balcon', 'pardoseală_de_lemn_sau_parchet',
    'aparat_pentru_prepararea_de_ceai/cafea', 'zonă_de_luat_masa', 'canale_prin_cablu', 'aer_condiţionat',
    'masă', 'suport_de_haine', 'cadă_sau_duş', 'frigider'
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
model_rf_optimized.fit(features_train_scaled, target_train_optimized.to_numpy())

# Modelul de recomandare (KMeans)
kmeans = KMeans(n_clusters=5, n_init='auto')
kmeans.fit(df[['price', 'nota_personal', 'nota_facilităţi', 'nota_curăţenie', 'nota_confort',
               'nota_raport_calitate/preţ', 'nota_locaţie', 'nota_wifi_gratuit']])
df['cluster'] = kmeans.labels_


def calculate_price_rating(predicted_price, actual_price, mae_half):
    if actual_price < predicted_price - 2 * mae_half:
        return "Very good price"
    elif predicted_price - 2 * mae_half <= actual_price < predicted_price - mae_half:
        return "Good price"
    elif predicted_price - mae_half <= actual_price <= predicted_price + mae_half:
        return "Fair price"
    elif predicted_price + mae_half < actual_price <= predicted_price + 2 * mae_half:
        return "Increased price"
    else:
        return "High price"


def predict_price_for_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        property_item = Property.query.get_or_404(room.property_id)

        # Calcularea numărului total de recenzii pentru proprietatea respectivă
        total_reviews = db.session.query(db.func.count(Review.id)).filter_by(property_id=property_item.id).scalar()

        input_data = {
            'persons': room.persons,
            'stars': property_item.stars,
            'num_reviews': total_reviews,
            f'type_{property_item.type.value}': True,
            f'region_{property_item.region}': True,
            f'room_type_{room.room_type}': True
        }

        for facility in room.facilities:
            input_data[facility.facility.name.lower().replace(' ', '_')] = True

        for column in selected_columns:
            if column not in input_data:
                input_data[column] = False

        input_features = np.array([input_data[col] for col in selected_columns]).reshape(1, -1)
        input_features = imputer.transform(input_features)
        input_features = scaler.transform(input_features)
        predicted_price = model_rf_optimized.predict(input_features)[0]

        mae_half = 36.40
        actual_price = room.price
        price_rating = calculate_price_rating(predicted_price, actual_price, mae_half)

        room.price_rating = price_rating
        db.session.commit()

        return {
            'price_rating': price_rating,
            'predicted_price': predicted_price
        }

    except Exception as e:
        return {'error': str(e)}


def recommend_properties(user_id, user_ratings, max_budget=None, preferred_region=None, check_in_date=None, check_out_date=None):
    try:
        # Obținem lista de cazări favorite ale utilizatorului curent
        favorite_properties = Favorite.query.filter_by(user_id=user_id).all()
        favorite_property_ids = [favorite.property_id for favorite in favorite_properties]

        # Obținem detaliile proprietăților favorite
        preferred_accommodations = [Property.query.get(fav_id).name for fav_id in favorite_property_ids]

        # Calculăm scorul de preferință pentru fiecare hotel
        for index, row in df.iterrows():
            preference_score = 0
            for category, user_rating in user_ratings.items():
                preference_score += row[category] * user_rating
            df.loc[index, 'preference_score'] = preference_score

        # Identificăm clusterul preferat
        if preferred_accommodations:
            preferred_cluster = df[df['name'].isin(preferred_accommodations)]['cluster'].mode()[0]

            # Filtrăm DataFrame-ul pentru a include doar hotelurile din clusterul preferat
            df_filtered = df[df['cluster'] == preferred_cluster]
        else:
            df_filtered = df.copy()

        # Aplicăm filtrele
        if max_budget:
            df_filtered = df_filtered[df_filtered['price'] <= max_budget]
        if preferred_region:
            df_filtered = df_filtered[df_filtered['region'] == preferred_region]

        # Identificăm facilitățile care sunt disponibile la cazări preferate
        if preferred_accommodations:
            preferred_facilities = df[df['name'].isin(preferred_accommodations)].iloc[:, -37:].sum(axis=0)

            # Calculăm scorul de potrivire a facilităților pentru fiecare hotel
            for index, row in df_filtered.iterrows():
                matching_facilities_score = sum(row[-37:] * preferred_facilities)
                df_filtered.loc[index, 'preference_score'] += matching_facilities_score

        # Obținem lista de camere rezervate în perioada specificată
        reserved_rooms = db.session.query(Reservation.room_id).filter(
            Reservation.check_in_date < check_out_date,
            Reservation.check_out_date > check_in_date
        ).subquery()

        # Filtrăm proprietățile care au camere disponibile
        available_properties_ids = db.session.query(Room.property_id).filter(
            ~Room.id.in_(reserved_rooms)
        ).distinct().all()
        available_properties_ids = [item[0] for item in available_properties_ids]

        df_filtered = df_filtered[df_filtered['id'].isin(available_properties_ids)]

        # Afișăm primele 5 hoteluri cu cel mai mare scor de preferință
        recommendations = df_filtered.nlargest(5, 'preference_score')

        return recommendations.to_dict(orient='records')

    except Exception as e:
        return {'error': str(e)}
