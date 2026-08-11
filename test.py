print("=== TEST VERSION 2 ===")

import osmnx as ox
import networkx as nx
import folium
import webbrowser

from campus_orte import ORTE
import campus_orte

from transformers import pipeline

# Lade ein kleines, kostenloses Modell (z.B. "tiiuae/falcon-7b-instruct")
generator = pipeline("text-generation", model="tiiuae/falcon-7b-instruct")

user_input = input("Deine Frage: ")
result = generator(user_input, max_new_tokens=100)
print("Antwort:", result[0]['generated_text'])

print(campus_orte.__file__)


# -------------------------------------------------
# 1. Graph laden
# -------------------------------------------------

print("Lade Kartendaten...")

G = ox.graph_from_xml("map-3.osm")

print("Kartendaten geladen.")



# -------------------------------------------------
# 2. Orte aus lokaler Datei laden
# -------------------------------------------------

orte = ORTE
print("TEST: Lokale Orte geladen:", len(orte))

# -------------------------------------------------
# 3. Gefundene Orte anzeigen
# -------------------------------------------------

print()
print("Gefundene Orte:")
print("----------------")

for ort in sorted(orte.keys()):
    print(ort)

print()
print("Anzahl Orte:", len(orte))



# -------------------------------------------------
# 4. Ort suchen (auch Teilnamen möglich)
# -------------------------------------------------

def finde_ort(suchbegriff):

    suchbegriff = suchbegriff.lower()


    # exakter Treffer
    for name in orte:

        if name.lower() == suchbegriff:
            return orte[name]


    # Teiltreffer
    for name in orte:

        if suchbegriff in name.lower():

            print(
                "Verwende gefundenen Ort:",
                name
            )

            return orte[name]


    return None



# -------------------------------------------------
# 5. Start und Ziel
# -------------------------------------------------

start_ort = "Mensa"
ziel_ort = "Hochschulsport"


start = finde_ort(start_ort)
ziel = finde_ort(ziel_ort)



if start is None:
    raise Exception(
        f"Startort '{start_ort}' wurde nicht gefunden."
    )


if ziel is None:
    raise Exception(
        f"Zielort '{ziel_ort}' wurde nicht gefunden."
    )



# Koordinaten

start_lat, start_lon = start
ziel_lat, ziel_lon = ziel



# -------------------------------------------------
# 6. Passende Knoten im Straßennetz finden
# -------------------------------------------------

print()
print("Suche Wegpunkte...")


orig = ox.nearest_nodes(
    G,
    start_lon,
    start_lat
)


dest = ox.nearest_nodes(
    G,
    ziel_lon,
    ziel_lat
)



# -------------------------------------------------
# 7. Kürzeste Route berechnen
# -------------------------------------------------

print("Berechne Route...")


route = nx.shortest_path(
    G,
    orig,
    dest,
    weight="length"
)



# -------------------------------------------------
# 8. Karte erzeugen
# -------------------------------------------------

print("Erstelle Karte...")


karte = folium.Map(
    location=[start_lat, start_lon],
    zoom_start=17
)



# Route als Koordinatenliste

route_coords = []


for node in route:

    y = G.nodes[node]["y"]
    x = G.nodes[node]["x"]

    route_coords.append(
        (y, x)
    )



# Route zeichnen

folium.PolyLine(
    route_coords,
    color="blue",
    weight=6,
    opacity=0.8
).add_to(karte)



# Startmarker

folium.Marker(
    [start_lat, start_lon],
    popup=f"Start: {start_ort}",
    icon=folium.Icon(
        color="green",
        icon="play"
    )
).add_to(karte)



# Zielmarker

folium.Marker(
    [ziel_lat, ziel_lon],
    popup=f"Ziel: {ziel_ort}",
    icon=folium.Icon(
        color="red",
        icon="flag"
    )
).add_to(karte)



# Karte speichern

karte.save("route.html")


webbrowser.open("route.html")


print()
print("✅ Route erfolgreich gespeichert.")
print("Öffne jetzt die Datei 'route.html' im Browser.")