import logging
import yaml
import math
import matplotlib.pyplot as plt

#############
### Input ###
#############

# Parse config
with open('./config.yaml', 'r') as stream:
  try:
    config = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)
    exit(1)

logging.basicConfig()
logger = logging.getLogger(__name__)
loglevel = config['loglevel']

match loglevel:
  case 'DEBUG':
    print('DEBUG')
    logger.setLevel(level=logging.DEBUG)
  case _:
    print('INFO')
    logger.setLevel(level=logging.INFO)

logger.info('')
logger.info('-------------')
logger.info('--- INPUT ---')
logger.info('-------------')
logger.info('')

# Kapital
eigenkapital = config['eigenkapital']
logger.info('eigenkapital: ' + str(config['eigenkapital']))
kaufpreis = config['kaufpreis']
logger.info('kaufpreis: ' + str(config['kaufpreis']))
modernisierung = config['modernisierung']
logger.info('modernisierung: ' + str(config['modernisierung']))

# Nebenkosten
grunderwerbsteuer = config['grunderwerbsteuer']
logger.info('grunderwerbsteuer: ' + str(config['grunderwerbsteuer']))
logger.info('notar: ' + str(config['notar']))
notar = config['notar']
makler = config['makler']
logger.info('makler: ' + str(config['makler']))

# Kredit
annuitat = config['annuitat']
logger.info('annuitat: ' + str(config['annuitat']))
zinssatzJahrlich = config['zinssatzJahrlich']
logger.info('zinssatzJahrlich: ' + str(config['zinssatzJahrlich']))
sollzinsbindungJahre = config['sollzinsbindungJahre']
logger.info('sollzinsbindungJahre: ' + str(config['sollzinsbindungJahre']))

# Miete
kaltMieteMonatlich = config['kaltMieteMonatlich']
logger.info('kaltMieteMonatlich: ' + str(config['kaltMieteMonatlich']))
mieteNebenkostenMonatlich = config['mieteNebenkostenMonatlich']
logger.info('mieteNebenkostenMonatlich: ' + str(config['mieteNebenkostenMonatlich']))
hausgeldMonatlich = config['hausgeldMonatlich']
logger.info('hausgeldMonatlich: ' + str(config['hausgeldMonatlich']))
steuerprozent = config['steuerprozent']
logger.info('steuerprozent: ' + str(config['steuerprozent']))

##################
### Berechnung ###
##################

logger.info('')
logger.info('------------------')
logger.info('--- BERECHNUNG ---')
logger.info('------------------')
logger.info('')

nebenkosten = kaufpreis * (grunderwerbsteuer + notar + makler)
logger.info('nebenkosten: ' + str(nebenkosten))
darlehen = kaufpreis + modernisierung + nebenkosten - eigenkapital
logger.info('darlehen: ' + str(darlehen))

zinssatzMonatlich = zinssatzJahrlich / 12.0
q = 1.0 + zinssatzMonatlich

laufzeitMonate = -math.log(1.0 - (darlehen * zinssatzMonatlich / annuitat)) / math.log(q)
logger.info('laufzeitMonaten: ' + str(laufzeitMonate))
logger.info('laufzeitJahre: ' + str(laufzeitMonate / 12.0))

anfangstilgung = annuitat * 12.0 / darlehen - zinssatzMonatlich
logger.info('anfangstilgung: ' + str(anfangstilgung))

nettoMieteEinkommenMonatlichVorSteuer = kaltMieteMonatlich + mieteNebenkostenMonatlich - hausgeldMonatlich
logger.info('nettoMieteEinkommenMonatlichVorSteuer: ' + str(nettoMieteEinkommenMonatlichVorSteuer))

# Plot variables
sollzinsbindungMonate = sollzinsbindungJahre * 12.0
jahreArray = []
restschuldenArray = []
zinsenArray = []
zinsenTotalArray = []
tilgungenArray = []
tilgungenTotalArray = []
immobilienEigentumTotalArray = []
nettoMieteEinkommenVorSteuerArray = []
nettoMieteEinkommenNachSteuerArray = []
nettoMieteEinkommenVorSteuerTotalArray = []
nettoMieteEinkommenNachSteuerTotalArray = []
selbstFinanzierungVonZinsenArray = []
selbstFinanzierungVonZinsenTotalArray = []
selbstFinanzierungInsgesamtArray = []
selbstFinanzierungInsgesamtTotalArray = []

zinsenBisSollzinsbindung = 0.0
zinsenBisEndeLaufzeit = 0.0
tilgungenBisSollzinsbindung = 0.0
tilgungenBisEndeLaufzeit = 0.0
immobilienEigentumBisEndeLaufzeit = eigenkapital
nettoMieteEinkommenBisSollzinsbindung = 0.0
nettoMieteEinkommenVorSteuerBisEndeLaufzeit = 0.0
nettoMieteEinkommenNachSteuerBisEndeLaufzeit = 0.0
selbstFinanzierungVonZinsenBisEndeLaufzeit = 0.0
selbstFinanzierungInsgesamtBisEndeLaufzeit = 0.0

for monat in range(int(laufzeitMonate)):

  logger.debug('---')

  # Zeit
  jahr = monat / 12.0
  jahreArray.append(jahr)
  logger.debug('jahr: ' + str(jahr))

  # Restschuld & Zins & Tilgung im Monat
  restschuld = darlehen * pow(q, monat) - annuitat * (pow(q, monat) - 1.0) / zinssatzMonatlich
  logger.debug('restschuld: ' + str(restschuld))
  zins = darlehen * (pow(q, laufzeitMonate) - pow(q, monat - 1.0)) / (pow(q, laufzeitMonate) - 1.0) * zinssatzMonatlich
  logger.debug('zins: ' + str(zins))
  tilgung = darlehen * pow(q, monat - 1.0) * zinssatzMonatlich / (pow(q, laufzeitMonate) - 1.0)
  logger.debug('tilgung: ' + str(tilgung))

  restschuldenArray.append(restschuld)
  zinsenArray.append(zins)
  tilgungenArray.append(tilgung)

  # Kumulativ bezahlten Zinsen & Tilgungen
  zinsenBisEndeLaufzeit = zinsenBisEndeLaufzeit + zins
  tilgungenBisEndeLaufzeit = tilgungenBisEndeLaufzeit + tilgung

  zinsenTotalArray.append(zinsenBisEndeLaufzeit)
  tilgungenTotalArray.append(tilgungenBisEndeLaufzeit)

  # Kumulativ bezahlten Zinsen & Tilgungen bis Ende der Sollzinsbindungszeit
  if monat < sollzinsbindungMonate:
    zinsenBisSollzinsbindung = zinsenBisSollzinsbindung + zins
    tilgungenBisSollzinsbindung = tilgungenBisSollzinsbindung + tilgung
    nettoMieteEinkommenBisSollzinsbindung = nettoMieteEinkommenBisSollzinsbindung + nettoMieteEinkommenMonatlichVorSteuer

  # Immobilieneigentum
  immobilienEigentumBisEndeLaufzeit = immobilienEigentumBisEndeLaufzeit + tilgung
  immobilienEigentumTotalArray.append(immobilienEigentumBisEndeLaufzeit / (kaufpreis + nebenkosten) * 100)

  # Mieteinkommen
  nettoMieteEinkommenVorSteuerArray.append(nettoMieteEinkommenMonatlichVorSteuer)
  nettoMieteEinkommenVorSteuerBisEndeLaufzeit = nettoMieteEinkommenVorSteuerBisEndeLaufzeit + nettoMieteEinkommenMonatlichVorSteuer
  nettoMieteEinkommenVorSteuerTotalArray.append(nettoMieteEinkommenVorSteuerBisEndeLaufzeit)

  # Selbst Finanzierung
  nettoMieteEinkommenMonatlichNachSteuer = (nettoMieteEinkommenMonatlichVorSteuer - zins) * (100.0 - steuerprozent) / 100.0
  logger.debug('nettoMieteEinkommenMonatlichNachSteuer: ' + str(nettoMieteEinkommenMonatlichNachSteuer))

  if nettoMieteEinkommenMonatlichNachSteuer < 0.0000001:
    nettoMieteEinkommenMonatlichNachSteuer = 0.0
    nettoMieteEinkommenNachSteuerArray.append(nettoMieteEinkommenMonatlichNachSteuer)

    nettoMieteEinkommenNachSteuerBisEndeLaufzeit = nettoMieteEinkommenNachSteuerBisEndeLaufzeit + nettoMieteEinkommenMonatlichNachSteuer
    nettoMieteEinkommenNachSteuerTotalArray.append(nettoMieteEinkommenNachSteuerBisEndeLaufzeit)

    selbstFinanzierungVonZinsen = zins - nettoMieteEinkommenMonatlichVorSteuer
    selbstFinanzierungVonZinsenArray.append(selbstFinanzierungVonZinsen)

    selbstFinanzierungVonZinsenBisEndeLaufzeit = selbstFinanzierungVonZinsenBisEndeLaufzeit + selbstFinanzierungVonZinsen
    selbstFinanzierungVonZinsenTotalArray.append(selbstFinanzierungVonZinsenBisEndeLaufzeit)

    selbstFinanzierungInsgesamt = tilgung + selbstFinanzierungVonZinsen
    selbstFinanzierungInsgesamtArray.append(selbstFinanzierungInsgesamt)

    selbstFinanzierungInsgesamtBisEndeLaufzeit = selbstFinanzierungInsgesamtBisEndeLaufzeit + selbstFinanzierungInsgesamt
    selbstFinanzierungInsgesamtTotalArray.append(selbstFinanzierungInsgesamtBisEndeLaufzeit)
  else:
    nettoMieteEinkommenNachSteuerArray.append(nettoMieteEinkommenMonatlichNachSteuer)

    nettoMieteEinkommenNachSteuerBisEndeLaufzeit = nettoMieteEinkommenNachSteuerBisEndeLaufzeit + nettoMieteEinkommenMonatlichNachSteuer
    nettoMieteEinkommenNachSteuerTotalArray.append(nettoMieteEinkommenNachSteuerBisEndeLaufzeit)

    selbstFinanzierungVonZinsen = 0.0
    selbstFinanzierungVonZinsenArray.append(selbstFinanzierungVonZinsen)

    selbstFinanzierungVonZinsenBisEndeLaufzeit = 0.0
    selbstFinanzierungVonZinsenTotalArray.append(selbstFinanzierungVonZinsenBisEndeLaufzeit)

    selbstFinanzierungInsgesamt = tilgung - nettoMieteEinkommenMonatlichNachSteuer
    selbstFinanzierungInsgesamtArray.append(selbstFinanzierungInsgesamt)

    selbstFinanzierungInsgesamtBisEndeLaufzeit = selbstFinanzierungInsgesamtBisEndeLaufzeit + selbstFinanzierungInsgesamt
    selbstFinanzierungInsgesamtTotalArray.append(selbstFinanzierungInsgesamtBisEndeLaufzeit)

logger.info('')
logger.info('----------------')
logger.info('--- ERGEBNIS ---')
logger.info('----------------')
logger.info('')

logger.info('zinsenBezahltBisSollzinsbindung: ' + str(zinsenBisSollzinsbindung))
logger.info('tilgungenBezahltBisSollzinsbindung: ' + str(tilgungenBisSollzinsbindung))
logger.info('nettoMieteEinkommenBezahltBisSollzinsbindung: ' + str(nettoMieteEinkommenBisSollzinsbindung))

# Verlorenes Geld = Zinsen + Nebenkosten + Modernisierung
verlorenesGeld = zinsenBisSollzinsbindung + nebenkosten + modernisierung
logger.info('verlorenesGeld: ' + str(verlorenesGeld))

immobilienEigentumAmZinsbindung = eigenkapital + tilgungenBisSollzinsbindung
immobilienEigentumAmZinsbindungProzent = immobilienEigentumAmZinsbindung / (kaufpreis + nebenkosten) * 100
logger.info('immobilienEigentumAmZinsbindung: ' + str(immobilienEigentumAmZinsbindung))
logger.info('immobilienEigentumAmZinsbindungProzent: ' + str(immobilienEigentumAmZinsbindungProzent))
logger.info('---')

######################
### Visualisierung ###
######################

# Restschuld
plt.title('Restschuld (€)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahreArray, restschuldenArray, label='Restschuld')
plt.plot(jahreArray, tilgungenTotalArray, label='Tilgung')
plt.legend()
plt.figure()

# Monatliche Betrachtung (€)
plt.title('Monatliche Betrachtung (€)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.ylim(0.0, annuitat * 1.1)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.axhline(y = annuitat, linestyle='--', color = 'g', label = 'Annuitat')
plt.plot(jahreArray, zinsenArray, label='Zinsen')
plt.plot(jahreArray, tilgungenArray, label='Tilgung')
plt.plot(jahreArray, nettoMieteEinkommenVorSteuerArray, label='Miete (vor Steuer)')
plt.plot(jahreArray, nettoMieteEinkommenNachSteuerArray, label='Miete (nach Steuer)')
plt.plot(jahreArray, selbstFinanzierungVonZinsenArray, label='Selbst finanziert (Zinsen)')
plt.plot(jahreArray, selbstFinanzierungInsgesamtArray, label='Selbst finanziert (Insgesamt)')
plt.legend()
plt.figure()

# Kumulative Betrachtung (€)
plt.title('Kumulative Betrachtung (€)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahreArray, zinsenTotalArray, label='Zinsen')
plt.plot(jahreArray, nettoMieteEinkommenVorSteuerTotalArray, label='Miete (vor Steuer)')
plt.plot(jahreArray, nettoMieteEinkommenNachSteuerTotalArray, label='Miete (nach Steuer)')
plt.plot(jahreArray, selbstFinanzierungVonZinsenTotalArray, label='Selbst finanziert (Zinsen)')
plt.plot(jahreArray, selbstFinanzierungInsgesamtTotalArray, label='Selbst finanziert (Insgesamt)')
plt.legend()
plt.figure()

# Immobilieneigentum
plt.title('Immobilieneigentum (%)')
plt.xlabel('Jahre')

plt.grid(visible=True)
plt.axvline(x = sollzinsbindungJahre, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(jahreArray, immobilienEigentumTotalArray, label='Eigentum %')
plt.legend()

plt.show()
