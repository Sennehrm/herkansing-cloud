# Smart Sensor Gateway met Monitoring en Automatisatie

**Vak**: Cloud Computing  
**Student**: Senne Herman  
**Opleiding**: Bachelor Elektronica-ICT, VIVES  

---

## Overzicht van het project

In dit project is een IoT Gateway gebouwd met Docker Compose. Het systeem leest continu sensordata (joysticks en knoppen van een controller) in via MQTT, valideert en filtert deze data in Node-RED, slaat de metingen op in InfluxDB en toont alles op een live dashboard. Het beheer van de containers gebeurt via Portainer.

De architectuur bestaat uit 5 containers die draaien binnen een eigen bridge-netwerk (`sensor-net`):
1. **Mosquitto (MQTT Broker)**: Ontvangt en verdeelt de MQTT-berichten van de sensoren.
2. **Controller Simulator (Python)**: Stuurt elke 5 seconden willekeurige joystickposities (X en Y tussen 0 en 255) en knopstatussen door naar Mosquitto.
3. **Node-RED**: Ontvangt de MQTT-data, controleert of de waarden geldig zijn via een Function node en schrijft alleen correcte data door naar InfluxDB.
4. **InfluxDB (v2.7)**: Tijdreeksdatabase waarin alle metingen worden bewaard en gevisualiseerd.
5. **Portainer**: Webinterface om de status van alle containers en het netwerk te bekijken.

---

## Installatie en opstarten

Zorg ervoor dat Docker en Docker Compose geïnstalleerd zijn op het systeem.

### 1. Repository clonen en starten
Open een terminal en voer de volgende commando's uit:

```bash
git clone https://github.com/Sennehrm/herkansing-cloud.git
cd herkansing-cloud
docker compose up -d --build
```

Je kunt het project ook opstarten via het deployment-script:
* **Windows**: `.\deploy.bat`
* **Linux**: `./deploy.sh`
* **Makefile**: `make deploy`

---

## Toegang tot de interfaces

| Service | URL | Inloggegevens |
| :--- | :--- | :--- |
| **InfluxDB (Dashboard)** | http://localhost:8086 | Gebruiker: `admin` <br> Wachtwoord: `Admin123` |
| **Node-RED** | http://localhost:1880 | Geen inlog nodig |
| **Portainer** | http://localhost:9000 | Gebruiker: `admin` (wachtwoord zelf kiezen bij 1e keer opstarten) |
| **Mosquitto (MQTT)** | localhost:1883 | Anonieme toegang ingeschakeld |

---

## InfluxDB Dashboard bekijken

Het dashboard staat na het opstarten al direct klaar in InfluxDB onder de naam **Smart Controller Gateway**.

> **Belangrijk bij het openen van het dashboard:**  
> InfluxDB zet de auto-refresh standaard op pauze. Om de data live te zien binnenkomen:  
> 1. Klik rechtsboven in het dashboard op het **refresh-icoontje (↻)** en zet dit op **`5s`**.  
> 2. Zet de tijdfilter daarnaast op **`Past 5m`** (of `Past 15m`) zodat de live lijngrafieken mooi over het hele scherm lopen.

### Wat staat er op het dashboard:
* **Joystick 1 & Joystick 2 (Live)**: Twee lijngrafieken die realtime de X- en Y-as tonen.
* **Laatste Knop**: Toont de meest recent ingedrukte knop.
* **Gemiddelde Joystick 1 & 2 (1 uur)**: Berekent het gemiddelde van de X- en Y-waarden over het afgelopen uur.
* **Gemiddelde Joystick 1 & 2 (24 uur)**: Berekent het gemiddelde over de afgelopen 24 uur.

---

## Dataverwerking en validatie (Node-RED)

In Node-RED draait een op maat gemaakte Function node (`Validatie & Datalogica`). Deze voert de volgende controles uit:
* **Bereikcontrole**: Controleert of de X- en Y-waarden effectief getallen zijn en tussen 0 en 255 liggen. Ongeldige of ontbrekende waarden worden meteen weggegooid.
* **Knop mapping**: Zet de binnengekomen knopnaam (zoals A, B, X, Y, L1, R1, L2, R2) om naar een numeriek ID (0 t/m 7).
* **Filtering**: Onbekende knoppen of `UNKNOWN` statussen worden genegeerd en niet opgeslagen in de database.

De benodigde InfluxDB plugin (`node-red-contrib-influxdb`) wordt tijdens het bouwen van de container automatisch geïnstalleerd via de Dockerfile in de map `nodered`.

---

## Hoe de deployments werken (CI/CD)

Om het systeem snel en geautomatiseerd bij te werken bij code-aanpassingen, zijn er deployment-scripts meegeleverd:
* **Windows**: `.\deploy.bat`
* **Linux / VM**: `./deploy.sh`
* **Makefile**: `make deploy`

### Wat doet het deployment-script precies?
Wanneer je het script uitvoert, gebeurt het volgende automatisch achter elkaar:
1. **Nieuwe code ophalen**: `git pull origin main` haalt de laatste wijzigingen binnen vanaf GitHub.
2. **Containers herbouwen**: `docker compose build --no-cache` bouwt de containers opnieuw op basis van de nieuwe code.
3. **Containers herstarten**: `docker compose up -d --remove-orphans` herstart de services met de nieuwe versie, zonder dat data verloren gaat.
4. **Schijfruimte opruimen**: `docker image prune -f` verwijdert oude, ongebruikte Docker images zodat de schijf niet volloopt.
5. **Status tonen**: `docker compose ps` toont direct of alle 5 containers weer actief en gezond draaien.

### Waarom is dit CI/CD?
In plaats van handmatig containers te stoppen, mappen te kopiëren en commando's te typen, is één commando (`.\deploy.bat` of `make deploy`) voldoende om de hele stack automatisch bij te werken naar de nieuwste versie. In een productieomgeving kan dit script automatisch worden uitgevoerd via een GitHub Actions workflow zodra er code naar de `main` branch wordt gepusht.

---

## Reflectie

Tijdens het project zijn verschillende onderdelen van cloud computing en IoT gecombineerd:
* Het opzetten van containerized microservices in een geïsoleerd bridge-netwerk.
* Communicatie via MQTT tussen een Python-applicatie en Node-RED.
* Datavalidatie en datatransformatie vóór opslag in een time-series databank.
* Het visualiseren en aggregeren van data (gemiddelden per uur en per 24 uur) via Flux queries in InfluxDB.
* Het automatiseren van het bouw- en deploymentproces via Docker Compose en scripts.
