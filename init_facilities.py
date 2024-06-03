from app import db, create_app
from app.models import Facility

app = create_app()
app.app_context().push()

# Lista de facilități predefinite
facilities = [
    'Mic dejun', 'Vedere la oraș', 'Menaj zilnic', 'Canale prin satelit',
    'Zonă de luat masa în aer liber', 'Cadă', 'Facilităţi de călcat', 'Izolare fonică', 'terasă la soare',
    'Pardoseală de gresie/marmură', 'Papuci de casă', 'uscător de rufe', 'Animale de companie', 'Încălzire',
    'Birou', 'mobilier exterior', 'Alarmă de fum', 'Vedere la grădină', 'Cuptor', 'Cuptor cu microunde',
    'Zonă de relaxare', 'Canapea', 'Intrare privată', 'Fier de călcat', 'Mașină de cafea', 'Plită de gătit',
    'Extinctoare', 'Cană fierbător', 'grădină', 'Ustensile de bucătărie', 'Maşină de spălat', 'Balcon',
    'Pardoseală de lemn sau parchet', 'Aparat pentru prepararea de ceai/cafea', 'Zonă de luat masa',
    'Canale prin cablu', 'aer condiţionat', 'Masă', 'Suport de haine', 'Cadă sau duş', 'Frigider'
]

# Șterge toate facilitățile existente
db.session.query(Facility).delete()

# Adaugă facilitățile predefinite
for facility_name in facilities:
    new_facility = Facility(name=facility_name)
    db.session.add(new_facility)

db.session.commit()
print("Facilitățile predefinite au fost adăugate în baza de date.")
