import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from .models import Favorite, Property, Room, Review, db, Reservation


# Încărcarea și pregătirea datasetului
def load_and_prepare_data():
    df = pd.read_csv('clean_dataset_Romania.csv')

    # Codificarea one-hot
    df = pd.get_dummies(df, columns=['type', 'region', 'room_type'])

    # Creează o listă cu numele coloanelor codificate cu one-hot
    one_hot_columns = [col for col in df.columns if 'type_' in col or 'region_' in col or 'room_type_' in col]

    # Adaugă coloanele predefinite la listă
    selected_columns = one_hot_columns + [
        'persons', 'stars', 'nota_personal', 'nota_facilităţi', 'nota_curăţenie',
        'nota_confort', 'nota_raport_calitate/preţ', 'nota_locaţie', 'nota_wifi_gratuit', 'num_reviews',
        'vedere_la_oras', 'menaj_zilnic', 'canale_prin_satelit', 'zona_de_luat_masa_in_aer_liber', 'cada',
        'facilitati_de_calcat', 'izolare_fonica', 'terasa_la_soare', 'pardoseala_de_gresie/marmura', 'papuci_de_casa',
        'uscator_de_rufe', 'animale_de_companie', 'incalzire', 'birou', 'mobilier_exterior', 'alarma_de_fum',
        'vedere_la_gradina', 'cuptor', 'cuptor_cu_microunde', 'zona_de_relaxare', 'canapea', 'intrare_privata',
        'fier_de_calcat', 'masina_de_cafea', 'plita_de_gatit', 'extinctoare', 'cana_fierbator', 'gradina',
        'ustensile_de_bucatarie', 'masina_de_spalat', 'balcon', 'pardoseala_de_lemn_sau_parchet',
        'aparat_pentru_prepararea_de_ceai/cafea', 'zona_de_luat_masa', 'canale_prin_cablu', 'aer_conditionat', 'masa',
        'suport_de_haine', 'cada_sau_dus', 'frigider', 'mic_dejun'
    ]

    return df, selected_columns


# Funcția de actualizare a clusterelor
def update_property_clusters():
    df, selected_columns = load_and_prepare_data()

    # Modelul de recomandare (KMeans)
    kmeans = KMeans(n_clusters=5, n_init='auto')
    kmeans.fit(df[['price', 'nota_personal', 'nota_facilităţi', 'nota_curăţenie', 'nota_confort',
                   'nota_raport_calitate/preţ', 'nota_locaţie', 'nota_wifi_gratuit']])
    df['cluster'] = kmeans.labels_

    # Actualizarea valorilor cluster în baza de date folosind indexul DataFrame-ului
    properties = Property.query.all()
    for idx, property_item in enumerate(properties):
        property_item.cluster = df.at[idx, 'cluster']
    db.session.commit()


# Funcția de predicție a prețului pentru o cameră
def predict_price_for_room(room_id):
    try:
        df, selected_columns = load_and_prepare_data()

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
            f'room_type_{room.room_type}': True,
            'vedere_la_oras': room.vedere_la_oras,
            'menaj_zilnic': room.menaj_zilnic,
            'canale_prin_satelit': room.canale_prin_satelit,
            'zona_de_luat_masa_in_aer_liber': room.zona_de_luat_masa_in_aer_liber,
            'cada': room.cada,
            'facilitati_de_calcat': room.facilitati_de_calcat,
            'izolare_fonica': room.izolare_fonica,
            'terasa_la_soare': room.terasa_la_soare,
            'pardoseala_de_gresie_marmura': room.pardoseala_de_gresie_marmura,
            'papuci_de_casa': room.papuci_de_casa,
            'uscator_de_rufe': room.uscator_de_rufe,
            'animale_de_companie': room.animale_de_companie,
            'incalzire': room.incalzire,
            'birou': room.birou,
            'mobilier_exterior': room.mobilier_exterior,
            'alarma_de_fum': room.alarma_de_fum,
            'vedere_la_gradina': room.vedere_la_gradina,
            'cuptor': room.cuptor,
            'cuptor_cu_microunde': room.cuptor_cu_microunde,
            'zona_de_relaxare': room.zona_de_relaxare,
            'canapea': room.canapea,
            'intrare_privata': room.intrare_privata,
            'fier_de_calcat': room.fier_de_calcat,
            'masina_de_cafea': room.masina_de_cafea,
            'plita_de_gatit': room.plita_de_gatit,
            'extinctoare': room.extinctoare,
            'cana_fierbator': room.cana_fierbator,
            'gradina': room.gradina,
            'ustensile_de_bucatarie': room.ustensile_de_bucatarie,
            'masina_de_spalat': room.masina_de_spalat,
            'balcon': room.balcon,
            'pardoseala_de_lemn_sau_parchet': room.pardoseala_de_lemn_sau_parchet,
            'aparat_pentru_prepararea_de_ceai_cafea': room.aparat_pentru_prepararea_de_ceai_cafea,
            'zona_de_luat_masa': room.zona_de_luat_masa,
            'canale_prin_cablu': room.canale_prin_cablu,
            'aer_conditionat': room.aer_conditionat,
            'masa': room.masa,
            'suport_de_haine': room.suport_de_haine,
            'cada_sau_dus': room.cada_sau_dus,
            'frigider': room.frigider,
            'mic_dejun': room.mic_dejun
        }

        # Pregătirea modelului
        imputer = SimpleImputer(strategy='mean')
        scaler = StandardScaler()

        features = df[selected_columns]
        target = df['price']
        features = imputer.fit_transform(features)
        features = scaler.fit_transform(features)

        model_rf_optimized = RandomForestRegressor(random_state=0)
        model_rf_optimized.fit(features, target.to_numpy())

        input_features = np.array([input_data.get(col, False) for col in selected_columns]).reshape(1, -1)
        input_features = imputer.transform(input_features)
        input_features = scaler.transform(input_features)
        predicted_price = model_rf_optimized.predict(input_features)[0]

        mae_half = 35.00
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


# Funcția de recomandare a proprietăților
def recommend_properties(user_id, user_ratings, max_budget=None, preferred_region=None, check_in_date=None,
                         check_out_date=None):
    try:
        # Obținem lista de cazări favorite ale utilizatorului curent
        favorite_properties = Favorite.query.filter_by(user_id=user_id).all()
        favorite_property_ids = [favorite.property_id for favorite in favorite_properties]

        # Obținem detaliile proprietăților favorite
        preferred_accommodations = Property.query.filter(Property.id.in_(favorite_property_ids)).all()
        preferred_accommodation_names = [property.name for property in preferred_accommodations]

        # Construim DataFrame-ul din baza de date
        properties = Property.query.all()
        property_data = []
        for property in properties:
            property_dict = property.to_dict()
            for room in property.rooms:
                room_dict = room.to_dict()
                for col, value in room_dict.items():
                    if col not in property_dict:
                        property_dict[col] = value
            property_data.append(property_dict)

        df = pd.DataFrame(property_data)

        # Calculăm scorul de preferință pentru fiecare hotel
        for index, row in df.iterrows():
            preference_score = 0
            for category, user_rating in user_ratings.items():
                if category in row:
                    preference_score += row[category] * user_rating
            df.loc[index, 'preference_score'] = preference_score

        # Identificăm clusterul preferat
        if preferred_accommodations:
            preferred_cluster = df[df['name'].isin(preferred_accommodation_names)]['cluster'].mode()[0]

            # Filtrăm DataFrame-ul pentru a include doar hotelurile din clusterul preferat
            df_filtered = df[df['cluster'] == preferred_cluster]
        else:
            df_filtered = df.copy()

        # Aplicăm filtrele
        if max_budget:
            df_filtered = df_filtered[df_filtered['price'] <= max_budget]
        if preferred_region:
            df_filtered = df_filtered[df_filtered['region'] == preferred_region]

        # Definirea coloanelor de facilități
        facility_columns = [
            'vedere_la_oras', 'menaj_zilnic', 'canale_prin_satelit', 'zona_de_luat_masa_in_aer_liber', 'cada',
            'facilitati_de_calcat', 'izolare_fonica', 'terasa_la_soare', 'pardoseala_de_gresie_marmura',
            'papuci_de_casa',
            'uscator_de_rufe', 'animale_de_companie', 'incalzire', 'birou', 'mobilier_exterior', 'alarma_de_fum',
            'vedere_la_gradina', 'cuptor', 'cuptor_cu_microunde', 'zona_de_relaxare', 'canapea', 'intrare_privata',
            'fier_de_calcat', 'masina_de_cafea', 'plita_de_gatit', 'extinctoare', 'cana_fierbator', 'gradina',
            'ustensile_de_bucatarie', 'masina_de_spalat', 'balcon', 'pardoseala_de_lemn_sau_parchet',
            'aparat_pentru_prepararea_de_ceai/cafea', 'zona_de_luat_masa', 'canale_prin_cablu', 'aer_conditionat',
            'masa', 'suport_de_haine', 'cada_sau_dus', 'frigider', 'mic_dejun'
        ]

        # Verificăm dacă toate coloanele de facilități sunt disponibile în DataFrame
        available_facility_columns = [col for col in facility_columns if col in df.columns]

        if preferred_accommodations:
            preferred_facilities = df[df['name'].isin(preferred_accommodation_names)][available_facility_columns].sum(
                axis=0)

            # Calculăm scorul de potrivire a facilităților pentru fiecare hotel
            for index, row in df_filtered.iterrows():
                matching_facilities_score = sum(row[available_facility_columns] * preferred_facilities)
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
        recommendations_df = df_filtered.nlargest(5, 'preference_score')

        recommendations = []
        for _, row in recommendations_df.iterrows():
            recommendation = {
                'address': row['address'],
                'availability': row['availability'],
                'check_in': row['check_in'],
                'check_out': row['check_out'],
                'cluster': row['cluster'],
                'country': row['country'],
                'description': row['description'],
                'id': row['id'],
                'images': row['images'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'name': row['name'],
                'nota_confort': row['nota_confort'],
                'nota_curăţenie': row['nota_curăţenie'],
                'nota_facilităţi': row['nota_facilităţi'],
                'nota_locaţie': row['nota_locaţie'],
                'nota_personal': row['nota_personal'],
                'nota_raport_calitate/preţ': row['nota_raport_calitate/preţ'],
                'nota_wifi_gratuit': row['nota_wifi_gratuit'],
                'num_reviews': row['num_reviews'],
                'owner_id': row['owner_id'],
                'postal_code': row['postal_code'],
                'region': row['region'],
                'rooms': [
                    {
                        'currency': room.currency,
                        'persons': room.persons,
                        'price': room.price,
                        'room_type': room.room_type
                    } for room in Property.query.get(row['id']).rooms
                ],
                'stars': row['stars'],
                'total_persons': row['persons'],
                'total_price': row['price'],
                'type': row['type'],
                'preference_score': row['preference_score']
            }

            # Adăugăm facilitățile la recomandări
            for col in available_facility_columns:
                recommendation[col] = row[col]

            recommendations.append(recommendation)

        return recommendations

    except Exception as e:
        print(f"Error in recommend_properties: {str(e)}")
        return []
