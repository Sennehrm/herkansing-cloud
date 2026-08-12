# Herkansing cloud opdracht

## Overzicht van het Project

Dit project implementeert een containergebaseerde **Edge IoT Gateway-architectuur**. Het systeem leest continu industriële sensordata (joysticks en controllerknoppen) uit via MQTT, verwerkt en valideert de datastroom in Node-RED, slaat de tijdreeksmetingen op in InfluxDB en visualiseert deze in een live dashboard. Het volledige ecosysteem wordt georkestreerd met Docker Compose en beheerd via Portainer.

---

### Microservices:
1. **Mosquitto (`eclipse-mosquitto:2`)**: Centrale MQTT message broker die inkomende sensorberichten ontvangt en distribueert.
2. **Controller Simulator (Python 3.12)**: Simuleert een controller met 2 joysticks ($X, Y \in [0, 255]$) en knoppen (A, B, X, Y, L1, R1, L2, R2) en publiceert elke 5 seconden.
3. **Node-RED**: Ingest data via MQTT, voert datavalidatie en filtering uit in een zelfgeschreven Function Node en stuurt gevalideerde data door naar InfluxDB.
4. **InfluxDB 2.7**: Tijdreeksdatabase die metingen bewaart met timestamps en metadata.
5. **Portainer CE**: Beheerinterface voor realtime inzicht in containerstatussen, logging en resources.

---

## Volledig Geautomatiseerde Installatie (Zero-Config)

Het project is **100% plug-and-play**. Na het clonen start de hele keten automatisch op inclusief pre-installed plugins, tokens en dashboard:

### 1. Repository clonen & starten
```bash
git clone https://github.com/Sennehrm/herkansing-cloud.git
cd herkansing-cloud
docker compose up -d 
```

*Of via de CI/CD deployment scripts:*
* **Windows**: `.\deploy.bat`
* **Linux**: `./deploy.sh`
* **Makefile**: `make deploy`

---

## Technische Specificaties & Implementatie

### 1. Sensorcommunicatie (MQTT)
De simulator publiceert naar drie afzonderlijke topics:
* `sensor/controller/joystick1` ➔ `{"x": x1, "y": y1}`
* `sensor/controller/joystick2` ➔ `{"x": x2, "y": y2}`
* `sensor/controller/buttons` ➔ `"A"`, `"B"`, `"X"`, `"Y"`, `"L1"`, `"R1"`, `"L2"`, `"R2"`

### 2. Dataverwerking & Validatielogica (Node-RED)
In Node-RED draait de zelfgeschreven **Function Node** (`Validatie & Datalogica`):
* **Bereikvalidatie**: Controleert of $0 \le X, Y \le 255$. Foutieve of ontbrekende meetwaarden worden onmiddellijk gedropt (niet naar de databank geschreven).
* **Button Mapping**: Vertaalt de knoptekst naar een numeriek ID (0 t/m 7) en bewaart de naam als label.
* **Filtering**: Negeert ongeldige of `UNKNOWN` knoppen.
* **Auto-Provisioning**: De Node-RED container bouwt via `nodered/Dockerfile` automatisch de `node-red-contrib-influxdb` plugin in en laadt de flows en credentials zonder handmatige stappen.

### 3. Opslag & Dashboarding (InfluxDB)
Het dashboard staat na het opstarten al direct klaar in InfluxDB onder de naam **Smart Controller Gateway**:
* **Joystick 1 Live (X & Y)**: Realtime lijngrafiek van Joystick 1 uitslagen.
* **Joystick 2 Live (X & Y)**: Realtime lijngrafiek van Joystick 2 uitslagen.
* **Laatste Knop**: Toont live de laatst ingedrukte controllerknop.
* **Gemiddelde Joystick 1 & 2 (1 uur)**: Berekent het gemiddelde over het afgelopen 1 uur (`start: -1h`).
* **Gemiddelde Joystick 1 & 2 (24 uur)**: Berekent het gemiddelde over 24 uur (`start: -24h`).

> **Tip voor live visualisatie:**  
> InfluxDB zet de auto-refresh standaard op pauze. Klik rechtsboven in het dashboard op het refresh-icoontje (↻) en zet dit op **`5s`** en de tijdfilter op **`Past 5m`** om de data live te zien binnenstromen.

---

## Toegang tot Services & Credentials

| Service | URL | Gebruikersnaam | Wachtwoord |
| :--- | :--- | :--- | :--- |
| **InfluxDB Dashboard** | [http://localhost:8086](http://localhost:8086) | `admin` | `Admin123` |
| **Node-RED Flows** | [http://localhost:1880](http://localhost:1880) | - | *(Pre-geconfigureerd met token)* |
| **Portainer UI** | [http://localhost:9000](http://localhost:9000) | `admin` | *(In te stellen bij 1e opstart)* |
| **Mosquitto MQTT** | `localhost:1883` | - | *(Anonieme toegang toegestaan)* |

---

## CI/CD & Automatische Backup via GitHub

### 1. Deployment Scripts
Het project bevat geautomatiseerde deployment-scripts ([deploy.bat](deploy.bat), [deploy.sh](deploy.sh) en [makefile](makefile)) die het volledige CI/CD-principe demonstreren:
1. **`git pull origin main`**: Haalt de nieuwste broncode binnen vanaf GitHub.
2. **`docker compose build --no-cache`**: Herbouwt de gewijzigde applicatie-images schoon zonder oude build-cache.
3. **`docker compose up -d --remove-orphans`**: Rolt de nieuwe containers uit met minimale downtime.
4. **`docker image prune -f`**: Verwijdert ongebruikte 'dangling' images om schijfruimte vrij te houden.
5. **Health Check (`docker compose ps`)**: Valideert dat alle services actief en gezond draaien.

### 2. Automatische Rolling Backup via GitHub Actions
Er is een geautomatiseerde GitHub Actions workflow ingesteld (`.github/workflows/backup.yml`) met een 2-traps rotatiesysteem:
* Draait automatisch **elke 2 dagen** (en is handmatig te triggeren via het tabblad *Actions*).
* **`backup-latest`**: Bevat altijd de meest recente back-up van het project.
* **`backup-previous`**: Bevat de vorige back-up van 2 dagen geleden als extra herstelpunt.
* Bij elke nieuwe run schuift de huidige back-up automatisch door naar `backup-previous` (waardoor de oudste overschreven wordt) en wordt de nieuwe code opgeslagen in `backup-latest`. Hierdoor zijn er altijd **twee veilige herstelpunten** beschikbaar in GitHub.
