# Historische energie importeren via Home Assistant Recorder

Deze eerste opzet vervangt de directe SQL-schrijfroute voor één specifiek scenario:
**oudere historie toevoegen vóór een bestaande, correcte HA-reeks**.

De uitvoering blijft buiten Home Assistant. Een eigen integratie is niet nodig.
Het script gebruikt de WebSocket-opdrachten van Recorder en wijzigt geen databasebestanden.
Gebaseerd op de Core-code van **2026.10.1**. Er is geen live import uitgevoerd.

## Bestanden

- `import_energy.py`: converter, importplan, uitvoering en terugleescontrole.
- `config.example.json`: voorbeeldmapping van generieke bestandsnaam naar HA-sensor.
- `requirements.txt`: externe afhankelijkheid voor de WebSocket-verbinding.
- `test_import_energy.py`: offline gedragstests met een nagebootste HA-API.

## Formaat en grenzen

Gebruik hetzelfde generieke formaat als de repo, zonder header:

```text
1704067200,100000
1704070800,105000
1704074400,110000
```

De eerste kolom is UNIX-tijd in seconden. De tweede kolom is de cumulatieve
meterstand **aan het begin van het interval**, in de geconfigureerde bron-eenheid.
In dit voorbeeld is de meterstand om 00:00 100000 Wh, om 01:00 105000 Wh en
om 02:00 110000 Wh. Het verbruik is dus 5 kWh per uur. De eerste tellerstand
van 100 kWh wordt niet als nieuw verbruik geteld.

De laatste regel sluit het voorgaande interval af; het script verzint geen
verbruik ná die regel. De bron moet doorlopen tot ten minste het einde van
de tweede volledige HA-overlapuurperiode.

Bestandsnamen zijn `<import_name>_high_resolution.csv` en/of
`<import_name>_low_resolution.csv`. De bron-eenheid geldt voor alle bestanden
van dezelfde mapping. HIGH heeft voorrang; LOW wordt alleen vóór het eerste
HIGH-tijdstip gebruikt, zoals in de bestaande repo.

Deze opzet ondersteunt:

- Bestaande HA-sensoren met `has_sum=true`, `mean_type=0` en een recente
  vijfminutenreeks; energie, gas en water.
- Wh/kWh/MWh en L/m³. De opgeslagen statistiekeenheid van HA is leidend,
  niet de weergave-eenheid van de sensor.
- Tijdstippen op exacte UTC-uurgrenzen.
- Meerdere sensoren, afzonderlijk verwerkt en bijgehouden in het journaal.

Deze opzet ondersteunt nog geen lege of externe doelen, geen ruwe state-historie,
geen vervanging van overlappende HA-metingen en geen kwartierwaarden zonder
voorafgaande uurconversie. Het script zaait geen ontbrekende kortetermijnketen.

## De sum-aansluiting

Voor ieder broninterval wordt het verschil tussen opeenvolgende meterstanden
berekend. Daaruit ontstaat een cumulatieve bron-`sum`, beginnend bij het
verbruik van het eerste beschikbare interval.

Het script haalt de bestaande uurstatistieken en recente vijfminutenstatistieken
op en vindt het werkelijke eerste HA-uur. Alleen bronuren vóór dat eerste
HA-uur worden ingevoerd. De overlap wordt gebruikt om de aansluiting te toetsen.

De correctie is:

```text
correctie = berekende bron-sum op eerste HA-uur - bestaande HA-sum op dat uur
```

Het script toetst diezelfde correctie op alle beschikbare gedeelde uren vóór
de recente compileergrens. Het verschil moet binnen `overlap_tolerance` blijven.
Die tolerantie is absoluut en wordt opgegeven in de HA-statistiekeenheid.
De standaard is 0,02. Kies deze op basis van bronresolutie en afronding;
vergroot haar niet alleen om een waarschuwing weg te krijgen.

Voorbeeld:

| Uur | Bronstand aan begin, kWh | Berekende sum einde uur | HA-sum |
|---|---:|---:|---:|
| 00:00 | 100 | 5 | ontbreekt |
| 01:00 | 105 | 10 | ontbreekt |
| 02:00 | 110 | 12 | 2 |
| 03:00 | 112 | 15 | 5 |
| 04:00 | 115 | sluitregel | — |

De import schrijft de eerste twee uren met sums 5 en 10. De twee overlapuren
geven dezelfde correctie +10. De bestaande sums worden daarna 12 en 15.
De bestaande HA-meterstanden en verbruiksverschillen blijven intact.

Een bestaande hoge HA-baseline kan ook een negatieve correctie vereisen. Het
script telt daarom niet blind het historische eindtotaal bij HA op.

## Daggegevens, gaten en tellerresets

Standaard is `gap_policy` **reject**. Meer dan één uur tussen bronmetingen
leidt tot een stop, omdat er geen gemeten uurverdeling beschikbaar is.

Met expliciet `"gap_policy": "uniform"` wordt intervalverbruik gelijkmatig
over de ontbrekende uren verdeeld. Daggegevens leveren daarmee geschatte
uurwaarden op, geen gemeten uurwaarden. Het plan vermeldt het aantal geschatte
uren. Intervallen van meer dan 31 dagen worden geweigerd.

Standaard is `reset_policy` **reject**. Een dalende tellerstand stopt de import.
Met expliciet `"reset_policy": "zero"` wordt aangenomen dat de teller naar nul
is gereset en is de nieuwe stand het verbruik ná de reset. Verbruik vóór de
reset binnen dat interval is niet uit twee standen terug te halen. Dat is
een expliciete aanname, geen gegarandeerde correctie. Een reset in een
meeruursinterval wordt altijd geweigerd.

Ongeldige getallen, NaN, infinity, conflicterende dubbele tijdstippen, lege
velden, headers en negatieve tellerstanden worden geweigerd. Er wordt niets
automatisch op nul gezet.

## Gebruik op Windows

Voer deze opdrachten uit in de map waarin de bestanden staan.

```powershell
python -m pip install -r requirements.txt
```

Kopieer `config.example.json` naar bijvoorbeeld `config.json`, vul de echte
statistiek-ID's, eenheden en bestandspaden in. Relatieve CSV-paden worden
ten opzichte van het configuratiebestand gelezen.

Stel de verbinding en een administrator-token in voor de huidige sessie.
Het token wordt niet opgeslagen in het plan of journaal. Onderstaand voorbeeld
vraagt het token zonder het zichtbaar af te drukken:

```powershell
$env:HA_URL = 'http://homeassistant.local:8123'
$energyImportToken = Read-Host 'HA administrator-token' -MaskInput
$env:HA_TOKEN = $energyImportToken
```

`-MaskInput` vereist PowerShell 7. Gebruik in een oudere PowerShell een bestaande
veilige methode om de omgevingsvariabele in te stellen; zet het token niet in
het configuratiebestand of een gedeeld commando.

Maak eerst een plan:

```powershell
python import_energy.py plan --config config.json --output import-plan.json
```

Dit leest HA en schrijft alleen een lokaal JSON-bestand. De preview schrijft
**niets** naar Home Assistant. Bestaande planbestanden worden niet overschreven.

Controleer per sensor de bestemming, opgeslagen eenheid, tijdsgrens,
overlapafwijking, correctie, aannames en historische uurwaarden. Het plan bevat
ook de oorspronkelijke uitgelezen sums en standen als controlemateriaal.
Dit is geen volledige databaseback-up.

Na beoordeling en een databaseback-up kan een plan worden uitgevoerd:

```powershell
python import_energy.py apply --plan import-plan.json --backup-confirmed
```

Het script importeert in groepen van 500 uren. Na iedere groep worden de sums
en standen teruggelezen. Daarna voert het één sum-correctie uit vanaf het
eerste bestaande HA-uur. Uiteindelijk controleert het de historische uren,
de oorspronkelijke HA-uurreeks plus correctie en de opgeslagen recente
vijfminutenreeks plus correctie.

Recente uren worden tijdens planning buiten de controlesnapshot gehouden:
de grens ligt twee uur vóór het huidige UTC-uur. De correctieopdracht zelf
verschuift alle bestaande sums vanaf de aansluitgrens, ook nieuwere rijen.
Verificatie van toekomstige Recorder-cycli en een HA-herstart is nog een
live acceptatietest; die is in deze opzet niet uitgevoerd.

## Onderbreking, herhaling en herstel

Naast het plan ontstaat `import-plan.json.journal.json`, met per sensor de
fasen `importing`, `adjusting` en `complete`.

- Tijdens `importing` kan hetzelfde plan worden hervat. Al geschreven oudere
  uren moeten exact met het plan overeenkomen; opnieuw schrijven is daar
  deterministisch. De bestaande HA-uren moeten nog aan de oude snapshot voldoen.
- Vóór het versturen van de optellende correctie wordt `adjusting` duurzaam
  opgeslagen. Na een onderbreking leest het script eerst terug. Als de verwachte
  correctie zichtbaar is, wordt de sensor compleet gemeld zonder opnieuw op te tellen.
- Is de correctie niet bevestigd of slechts gedeeltelijk zichtbaar, dan stopt
  het script. Het verstuurt niet automatisch nogmaals een correctie. Inspecteer
  Recorder, plan en journaal; dit is bewust een situatie voor handmatige diagnose.
- Bij `complete` controleert herhaling alleen het resultaat en schrijft niets.

**Bewaar hetzelfde plan en journaal.** Een nieuw plan is geen vervanging voor
het hervatten van een gedeeltelijke import. Na 24 uur wordt verder schrijven
met een oud, nog niet gecorrigeerd plan geweigerd. Snapshots kunnen inmiddels
veranderd of gepurgd zijn. Inspecteer de reeds uitgevoerde stappen.

Een lockbestand voorkomt gelijktijdige uitvoeringen van hetzelfde plan. Een
procescrash kan de lock achterlaten: controleer eerst processen en journaal
voordat je die lock verwijdert. De lock beschermt niet tegen een ander plan,
een andere computer of wijzigingen door andere tools; voer die niet tegelijk uit.

De twee API-opdrachten vormen samen **geen transactie**. Tijdens import kan de
grafiek tijdelijk een niet-aangesloten reeks tonen. Het script biedt geen
automatische rollback. Een negatieve correctie is alleen een mogelijke
omkering van een bevestigde correctie, niet een volledig herstel van een import.
Voor volledig herstel is een passende databaseback-up nodig.

## Offline validatie

```powershell
python -m unittest -v test_import_energy
```

Er zijn 20 offline tests voor onder meer unitconversie, LOW/HIGH-voorrang,
sum-berekening, afwijkende overlap, tellerresets, dagverdeling, behoud van
bestaande meetwaarden, beide statistiektabellen, gedeeltelijke import,
verloren correctiebevestiging, dubbel uitvoeren, metadatawijzigingen en de
complete preview/uitvoering/journaalroute. De tests gebruiken een nagebootste
HA-API; ze bewijzen geen productiegeschiktheid op iedere Recorder-database.

## Bronnen

- [Recorder WebSocket-opdrachten, Core 2026.10.1](https://github.com/home-assistant/core/blob/2026.10.1/homeassistant/components/recorder/websocket_api.py)
- [Statistiekverwerking en sum-correctie, Core 2026.10.1](https://github.com/home-assistant/core/blob/2026.10.1/homeassistant/components/recorder/statistics.py)
- [Generieke bronimport, repo v2.9](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/tree/v2.9)
