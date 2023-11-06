# Lastenheft MMISP Backend

Webseiten:
* https://www.misp-project.org/
* https://github.com/MISP/MISP
* API Spec: https://www.misp-project.org/openapi/

## API Spec

* 130 Endpunkte (`yq '.paths | keys | length' openapi.yaml`)

## MUSS-Anforderungen

* Login via Username/Passwort
* Login via OIDC
* Datenbank Kompatibilität mit MISP
* Implementierung der API Endpunkte für:
    * Events
    * Galaxies
    * Attributes
    * Sharing Groups
    * Objects
    * Sightings
    * Tags
    * Taxonomies
* Qualitätsanforderung:
    * alle Funktionen mit Type Annotations

## SOLL-Anforderungen

* Implementierung der API Endpunkte für:
    * Feeds
    * Warninglists
    * Noticelists
    * Auth Keys
    * User Settings
* Read-Only Modus
* async Programmierung für Datenbankzugriff

## KANN-Anforderungen

* Konfiguration vollständig über environment Variablen möglich
* Ausgabe in anderen Formaten als JSON
    * stix, stix2
    * xml
    * csv
    * siehe `X-Response-Format`