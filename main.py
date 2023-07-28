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
zinsbindungJahre = config['zinsbindungJahre']
logger.info("zinsbindungJahre: " + str(config['zinsbindungJahre']))

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

laufzeitMonaten = -math.log(1.0 - (darlehen * zinssatzMonatlich / annuitat)) / math.log(q)
logger.info("laufzeitMonaten: " + str(laufzeitMonaten))
logger.info("laufzeitJahre: " + str(laufzeitMonaten / 12.0))

anfangstilgung = annuitat * 12.0 / darlehen - zinssatzMonatlich
logger.info("anfangstilgung: " + str(anfangstilgung))

# Plot variables
zinsbindungMonate = zinsbindungJahre * 12.0
jahre = []
restschulden = []
zinsen = []
zinsenTotal = []
tilgungen = []
tilgungenTotal = []
immobilienEigentum = []

zinsBezahlt = 0.0
zinsTotal = 0.0
tilgungBezahlt = 0.0
tilgungTotal = 0.0
immobilienEigentumTotal = eigenkapital

for monat in range(int(laufzeitMonaten)):

  logger.debug("---")

  # Time
  jahr = monat / 12.0
  jahre.append(jahr)
  logger.debug("jahr: " + str(jahr))

  restschuld = darlehen * pow(q, monat) - annuitat * (pow(q, monat) - 1.0) / zinssatzMonatlich
  logger.debug("restschuld: " + str(restschuld))
  zins = darlehen * (pow(q, laufzeitMonaten) - pow(q, monat - 1.0)) / (pow(q, laufzeitMonaten) - 1.0) * zinssatzMonatlich
  logger.debug("zins: " + str(zins))
  tilgung = darlehen * pow(q, monat - 1.0) * zinssatzMonatlich / (pow(q, laufzeitMonaten) - 1.0)
  logger.debug("tilgung: " + str(tilgung))

  zinsTotal = zinsTotal + zins
  tilgungTotal = tilgungTotal + tilgung

  restschulden.append(restschuld)
  zinsen.append(zins)
  tilgungen.append(tilgung)
  
  zinsenTotal.append(zinsenTotal)
  tilgungenTotal.append(tilgungTotal)

  zinsTotal = zinsTotal + zins
  if monat < zinsbindungMonate:
    zinsBezahlt = zinsBezahlt + zins
    tilgungBezahlt = tilgungBezahlt + tilgung

  immobilienEigentumTotal = immobilienEigentumTotal + tilgung
  immobilienEigentum.append(immobilienEigentumTotal / (kaufpreis + nebenkosten) * 100)

logger.info('')
logger.info('----------------')
logger.info('--- ERGEBNIS ---')
logger.info('----------------')
logger.info('')

logger.info("zinsBezahlt: " + str(zinsBezahlt))
logger.info("tilgungBezahlt: " + str(tilgungBezahlt))
immobilienEigentumAmZinsbindung = eigenkapital + tilgungBezahlt
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
plt.axvline(x = zinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahre, restschulden, label="Restschuld")
plt.plot(jahre, tilgungenTotal, label="Tilgung")
plt.legend()
plt.figure()

# Zins & Tilgung (monatlich)
plt.title('Zins & Tilgung (€/monat)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.ylim(0.0, annuitat * 1.1)
plt.axvline(x = zinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.axhline(y = annuitat, linestyle='--', color = 'g', label = 'Annuitat')
plt.plot(jahre, zinsen, label="Zinsen")
plt.plot(jahre, tilgungen, label="Tilgung")
plt.legend()
plt.figure()

# Immobilieneigentum
plt.title('Immobilieneigentum (%)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = zinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahre, immobilienEigentum, label="Eigentum %")
plt.legend()

plt.show()
