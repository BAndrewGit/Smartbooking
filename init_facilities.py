from app import db, create_app
from app.models import Facility

app = create_app()
app.app_context().push()

# Lista de facilități predefinite
facilities = [
    'mic_dejun', 'vedere_la_oraș', 'menaj_zilnic', 'canale_prin_satelit',
    'zonă_de_luat_masa_în_aer_liber', 'cadă', 'facilităţi_de_călcat', 'izolare_fonică', 'terasă_la_soare',
    'pardoseală_de_gresie/marmură', 'papuci_de_casă', 'uscător_de_rufe', 'animale_de_companie', 'încălzire',
    'birou', 'mobilier_exterior', 'alarmă_de_fum', 'vedere_la_grădină', 'cuptor', 'cuptor_cu_microunde',
    'zonă_de_relaxare', 'canapea', 'intrare_privată', 'fier_de_călcat', 'mașină_de_cafea', 'plită_de_gătit',
    'extinctoare', 'cană_fierbător', 'grădină', 'ustensile_de_bucătărie', 'maşină_de_spălat', 'balcon',
    'pardoseală_de_lemn_sau_parchet', 'aparat_pentru_prepararea_de_ceai/cafea', 'zonă_de_luat_masa',
    'canale_prin_cablu', 'aer_condiţionat', 'masă', 'suport_de_haine', 'cadă_sau_duş', 'frigider'
]

# Șterge toate facilitățile existente
db.session.query(Facility).delete()

# Adaugă facilitățile predefinite
for facility_name in facilities:
    new_facility = Facility(name=facility_name)
    db.session.add(new_facility)

db.session.commit()
print("Facilitățile predefinite au fost adăugate în baza de date.")
