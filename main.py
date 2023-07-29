import logging
import yaml
import math
import matplotlib.pyplot as plt

#############
### Input ###
#############

# Parse config
with open("./config.yaml", "r") as stream:
  try:
    config = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)
    exit(1)

logging.basicConfig()
logger = logging.getLogger(__name__)
loglevel = config['loglevel']

match loglevel:
  case "DEBUG":
    print("DEBUG")
    logger.setLevel(level=logging.DEBUG)
  case _:
    print("INFO")
    logger.setLevel(level=logging.INFO)

logger.info('')
logger.info('-------------')
logger.info('--- INPUT ---')
logger.info('-------------')
logger.info('')

# Kapital
eigenkapital = config['eigenkapital']
logger.info("eigenkapital: " + str(config['eigenkapital']))
kaufpreis = config['kaufpreis']
logger.info("kaufpreis: " + str(config['kaufpreis']))
modernisierung = config['modernisierung']
logger.info("modernisierung: " + str(config['modernisierung']))

# Nebenkosten
grunderwerbsteuer = config['grunderwerbsteuer']
logger.info("grunderwerbsteuer: " + str(config['grunderwerbsteuer']))
logger.info("notar: " + str(config['notar']))
notar = config['notar']
makler = config['makler']
logger.info("makler: " + str(config['makler']))

# Kredit
annuitat = config['annuitat']
logger.info("annuitat: " + str(config['annuitat']))
zinssatzJahrlich = config['zinssatzJahrlich']
logger.info("zinssatzJahrlich: " + str(config['zinssatzJahrlich']))
sollzinsbindungJahre = config['sollzinsbindungJahre']
logger.info("sollzinsbindungJahre: " + str(config['sollzinsbindungJahre']))

# Miete
kaltMieteMonatlich = config['kaltMieteMonatlich']
logger.info("kaltMieteMonatlich: " + str(config['kaltMieteMonatlich']))
mieteNebenkostenMonatlich = config['mieteNebenkostenMonatlich']
logger.info("mieteNebenkostenMonatlich: " + str(config['mieteNebenkostenMonatlich']))
hausgeldMonatlich = config['hausgeldMonatlich']
logger.info("hausgeldMonatlich: " + str(config['hausgeldMonatlich']))

##################
### Berechnung ###
##################

logger.info('')
logger.info('------------------')
logger.info('--- BERECHNUNG ---')
logger.info('------------------')
logger.info('')

nebenkosten = kaufpreis * (grunderwerbsteuer + notar + makler)
logger.info("nebenkosten: " + str(nebenkosten))
darlehen = kaufpreis + modernisierung + nebenkosten - eigenkapital
logger.info("darlehen: " + str(darlehen))

zinssatzMonatlich = zinssatzJahrlich / 12.0
q = 1.0 + zinssatzMonatlich

laufzeitMonate = -math.log(1.0 - (darlehen * zinssatzMonatlich / annuitat)) / math.log(q)
logger.info("laufzeitMonaten: " + str(laufzeitMonate))
logger.info("laufzeitJahre: " + str(laufzeitMonate / 12.0))

anfangstilgung = annuitat * 12.0 / darlehen - zinssatzMonatlich
logger.info("anfangstilgung: " + str(anfangstilgung))

nettoMieteEinkommenMonatlich = kaltMieteMonatlich + mieteNebenkostenMonatlich - hausgeldMonatlich
logger.info("nettoMieteEinkommenMonatlich: " + str(nettoMieteEinkommenMonatlich))

# Plot variables
sollzinsbindungMonate = sollzinsbindungJahre * 12.0
jahreArray = []
restschuldenArray = []
zinsenArray = []
zinsenTotalArray = []
tilgungenArray = []
tilgungenTotalArray = []
immobilienEigentumArray = []
nettoMieteEinkommenArray = []

zinsenBezahltBisSollzinsbindung = 0.0
zinsenTotalBisEndeLaufzeit = 0.0
tilgungenBezahltBisSollzinsbindung = 0.0
tilgungenTotalBisEndeLaufzeit = 0.0
immobilienEigentumTotalBisEndeLaufzeit = eigenkapital
nettoMieteEinkommenBezahltBisSollzinsbindung = 0.0
nettoMieteEinkommenTotalBisEndeLaufzeit = 0.0

for monat in range(int(laufzeitMonate)):

  logger.debug("---")

  # Zeit
  jahr = monat / 12.0
  jahreArray.append(jahr)
  logger.debug("jahr: " + str(jahr))

  # Restschuld & Zins & Tilgung im Monat
  restschuld = darlehen * pow(q, monat) - annuitat * (pow(q, monat) - 1.0) / zinssatzMonatlich
  logger.debug("restschuld: " + str(restschuld))
  zins = darlehen * (pow(q, laufzeitMonate) - pow(q, monat - 1.0)) / (pow(q, laufzeitMonate) - 1.0) * zinssatzMonatlich
  logger.debug("zins: " + str(zins))
  tilgung = darlehen * pow(q, monat - 1.0) * zinssatzMonatlich / (pow(q, laufzeitMonate) - 1.0)
  logger.debug("tilgung: " + str(tilgung))

  restschuldenArray.append(restschuld)
  zinsenArray.append(zins)
  tilgungenArray.append(tilgung)

  # Kumulativ bezahlten Zinsen & Tilgungen
  zinsenTotalBisEndeLaufzeit = zinsenTotalBisEndeLaufzeit + zins
  tilgungenTotalBisEndeLaufzeit = tilgungenTotalBisEndeLaufzeit + tilgung

  zinsenTotalArray.append(zinsenTotalBisEndeLaufzeit)
  tilgungenTotalArray.append(tilgungenTotalBisEndeLaufzeit)

  # Kumulativ bezahlten Zinsen & Tilgungen bis Ende der Sollzinsbindungszeit
  if monat < sollzinsbindungMonate:
    zinsenBezahltBisSollzinsbindung = zinsenBezahltBisSollzinsbindung + zins
    tilgungenBezahltBisSollzinsbindung = tilgungenBezahltBisSollzinsbindung + tilgung
    nettoMieteEinkommenBezahltBisSollzinsbindung = nettoMieteEinkommenBezahltBisSollzinsbindung + nettoMieteEinkommenMonatlich

  # Immobilieneigentum
  immobilienEigentumTotalBisEndeLaufzeit = immobilienEigentumTotalBisEndeLaufzeit + tilgung
  immobilienEigentumArray.append(immobilienEigentumTotalBisEndeLaufzeit / (kaufpreis + nebenkosten) * 100)

  # Netto Mieteinkommen
  nettoMieteEinkommenTotalBisEndeLaufzeit = nettoMieteEinkommenTotalBisEndeLaufzeit + nettoMieteEinkommenMonatlich
  nettoMieteEinkommenArray.append(nettoMieteEinkommenTotalBisEndeLaufzeit)

logger.info('')
logger.info('----------------')
logger.info('--- ERGEBNIS ---')
logger.info('----------------')
logger.info('')

logger.info("zinsenBezahltBisSollzinsbindung: " + str(zinsenBezahltBisSollzinsbindung))
logger.info("tilgungenBezahltBisSollzinsbindung: " + str(tilgungenBezahltBisSollzinsbindung))
logger.info("nettoMieteEinkommenBezahltBisSollzinsbindung: " + str(nettoMieteEinkommenBezahltBisSollzinsbindung))

# Verlorenes Geld = Zinsen + Nebenkosten + Modernisierung
verlorenesGeld = zinsenBezahltBisSollzinsbindung + nebenkosten + modernisierung
logger.info("verlorenesGeld: " + str(verlorenesGeld))

immobilienEigentumAmZinsbindung = eigenkapital + tilgungenBezahltBisSollzinsbindung
immobilienEigentumAmZinsbindungProzent = immobilienEigentumAmZinsbindung / (kaufpreis + nebenkosten) * 100
logger.info("immobilienEigentumAmZinsbindung: " + str(immobilienEigentumAmZinsbindung))
logger.info("immobilienEigentumAmZinsbindungProzent: " + str(immobilienEigentumAmZinsbindungProzent))
logger.info("---")

######################
### Visualisierung ###
######################

# Restschuld
plt.title('Restschuld (€)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahreArray, restschuldenArray, label="Restschuld")
plt.plot(jahreArray, tilgungenTotalArray, label="Tilgung")
plt.legend()
plt.figure()

# Zins & Tilgung (monatlich)
plt.title('Zins & Tilgung (€/monat)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.ylim(0.0, annuitat * 1.1)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.axhline(y = annuitat, linestyle='--', color = 'g', label = 'Annuitat')
plt.plot(jahreArray, zinsenArray, label="Zinsen")
plt.plot(jahreArray, tilgungenArray, label="Tilgung")
plt.legend()
plt.figure()

# Verdient & Verloren (€)
plt.title('Verdient & Verloren (€)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahreArray, zinsenTotalArray, label="Zinsen")
plt.plot(jahreArray, nettoMieteEinkommenArray, label="Miete")
plt.legend()
plt.figure()

# Immobilieneigentum
plt.title('Immobilieneigentum (%)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahreArray, immobilienEigentumArray, label="Eigentum %")
plt.legend()

plt.show()
