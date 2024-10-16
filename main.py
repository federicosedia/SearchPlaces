import requests
import time
import json
import signal
import sys
from math import cos, pi  # Importa cos e pi dal modulo math

# Inserisci la tua Google API Key
API_KEY = ''  # Sostituisci con la tua chiave API

# Centro di Berlino (coordinate)
location = '52.5200,13.4050'
radius = 500  # Raggio iniziale in metri
place_type = 'bar'  # Tipi di luoghi da cercare
max_radius = 10000  # Raggio massimo da cercare in metri
increment = 200  # Incremento del raggio in metri
request = 1  # Inizializza il contatore delle richieste

all_places = []  # Lista per raccogliere i luoghi trovati

def signal_handler(sig, frame):
    print('Interruzione ricevuta! Salvataggio dei dati...')
    save_places_to_file(all_places)  # Chiama la funzione per salvare i dati
    sys.exit(0)

# Funzione per salvare i dati in un file JSON
def save_places_to_file(places):
    structured_places = {}
    for place in places:
        place_name = place['name']
        structured_places[place_name] = {
            "address": place.get('address', "Indirizzo non disponibile"),
            "selectedHashtags": place.get('selectedHashtags', []),  # Usa i tipi correttamente estratti
            "mainCategory": place.get('mainCategory', "Categoria non disponibile"),  # Aggiunta della mainCategory
            "primartupe": place['primaryTypeDisplayName'],
            "primartaupe": place['primaryType'],
            "name": place['name'],
        }

    with open('berlin_places_partial_bar_400_1_bar_prova_2.json', 'w') as json_file:
        json.dump(structured_places, json_file, indent=4)

# Imposta il gestore per l'interruzione
signal.signal(signal.SIGINT, signal_handler)

# Funzione per ottenere i luoghi tramite l'API di Google Places
def get_places(location, radius, place_type, api_key, next_token=None):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': location,
        'radius': radius,
        'type': place_type,
        'key': api_key,
    }
    if next_token:
        params['pagetoken'] = next_token
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Errore nell'API: {response.status_code}")
        return None
    return response.json()

# Funzione per salvare i dati in un file JSON
def save_places_to_file(places):
    structured_places = {}
    for place in places:
        place_name = place['name']
        structured_places[place_name] = {
            "address": place.get('address', "Indirizzo non disponibile"),
            "selectedHashtags": place.get('selectedHashtags', []),
            "mainCategory": place.get('mainCategory', "Categoria non disponibile"),
            "primartupe": place.get('primartupe', "Tipo non disponibile"),  # Modificato per usare il metodo get
            "primartaupe": place.get('primartaupe', "Tipo non disponibile"),  # Modificato per usare il metodo get
            "name": place['name'],
        }

    with open('berlin_places_partial_bar_400_1_bar_prova_2.json', 'w') as json_file:
        json.dump(structured_places, json_file, indent=4)

# Funzione per estrarre i dati dei luoghi
def extract_place_data(place, api_key):
    place_id = place['place_id']

    # Verifica se "bar" è il tipo principale (primo nella lista)
    types = place.get('types', [])

    # Condizione per controllare se il tipo principale è "bar"
    if len(types) == 0 or types[0] != 'bar':
        return None  # Ignora il luogo se "bar" non è il tipo principale

    place_details = {
        "name": place.get('name', "Nome non disponibile"),
        "address": place.get('vicinity', "Indirizzo non disponibile"),
        "placeUid": place_id,
        "latitude": place['geometry']['location']['lat'],
        "longitude": place['geometry']['location']['lng'],
        "rating": place.get('rating', 0),
        "totalRatings": place.get('user_ratings_total', 0),
        "imageUrl": (
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={place['photos'][0]['photo_reference']}&key={api_key}"
            if 'photos' in place and place['photos'] else 'https://example.com/image.jpg'
        ),
        "openingHours": place.get('opening_hours', {}).get('weekday_text', []),
        "selectedHashtags": types,  # Estrai tutti i tipi di luogo
        # Verifica se 'primaryTypeDisplayName' e 'primaryType' sono presenti, altrimenti usa un valore predefinito
        "primartupe": place.get('primaryTypeDisplayName', "Tipo non disponibile"),
        "primartaupe": place.get('primaryType', "Tipo non disponibile"),
    }
    return place_details




# Funzione per eseguire la ricerca in una griglia di coordinate
def get_places_in_grid(api_key, location, radius, place_type, max_radius, increment):
    lat, lng = map(float, location.split(','))

    global request  # Usa la variabile globale request
    for r in range(radius, max_radius + increment, increment):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                request += 1
                new_lat = lat + (dx * (r / 111320))  # 1 grado di latitudine è circa 111.32 km
                new_lng = lng + (dy * (r / (111320 * abs(cos(lat * pi / 180)))))  # Adjust for longitude
                new_location = f"{new_lat},{new_lng}"
                print(f"Cercando luoghi a {new_location} con raggio {r} metri... e richiesta numero {request}")
                next_token = None

                while True:
                    response = get_places(new_location, r, place_type, api_key, next_token)

                    if response is None:
                        break

                    if 'results' in response:
                        for place in response['results']:
                            place_data = extract_place_data(place, api_key)

                            # Controlla se place_data non è None prima di aggiungerlo alla lista
                            if place_data and place_data['placeUid'] not in [p['placeUid'] for p in all_places]:
                                all_places.append(place_data)

                    if 'next_page_token' in response:
                        next_token = response['next_page_token']
                        time.sleep(2)  # Pausa di 2 secondi richiesta da Google per il next_page_token
                    else:
                        break

    return all_places

# Ottieni i luoghi
places = get_places_in_grid(API_KEY, location, radius, place_type, max_radius, increment)

# Salva i dati completi nel file finale
save_places_to_file(places)

# Stampa il numero totale di luoghi trovati
print(f"{len(all_places)} luoghi unici sono stati salvati in 'berlin_places_partial_bar_400_1_bar_prova_2.json'.")
