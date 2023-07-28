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

# Kapital
eigenkapital = config['eigenkapital']
print("eigenkapital: " + str(config['eigenkapital']))
kaufpreis = config['kaufpreis']
print("kaufpreis: " + str(config['kaufpreis']))
modernisierung = config['modernisierung']
print("modernisierung: " + str(config['modernisierung']))

# Nebenkosten
grunderwerbsteuer = config['grunderwerbsteuer']
print("grunderwerbsteuer: " + str(config['grunderwerbsteuer']))
print("notar: " + str(config['notar']))
notar = config['notar']
makler = config['makler']
print("makler: " + str(config['makler']))

# Kredit
annuitat = config['annuitat']
print("annuitat: " + str(config['annuitat']))
zinssatzJahrlich = config['zinssatzJahrlich']
print("zinssatzJahrlich: " + str(config['zinssatzJahrlich']))
zinsbindungJahre = config['zinsbindungJahre']
print("zinsbindungJahre: " + str(config['zinsbindungJahre']))

##################
### Berechnung ###
##################

nebenkosten = kaufpreis * (grunderwerbsteuer + notar + makler)
print("nebenkosten: " + str(nebenkosten))
darlehen = kaufpreis + modernisierung + nebenkosten - eigenkapital
print("darlehen: " + str(darlehen))

zinssatzMonatlich = zinssatzJahrlich / 12.0
q = 1.0 + zinssatzMonatlich

laufzeitMonaten = -math.log(1.0 - (darlehen * zinssatzMonatlich / annuitat)) / math.log(q)
print("laufzeitMonaten: " + str(laufzeitMonaten))
print("laufzeitJahre: " + str(laufzeitMonaten / 12.0))

anfangstilgung = annuitat * 12.0 / darlehen - zinssatzMonatlich
print("anfangstilgung: " + str(anfangstilgung))

# Plot variables
zinsbindungMonate = zinsbindungJahre * 12.0
monate = []
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

  print("---")

  # Time
  monate.append(monat)
  print("restschuld: " + str(monat))

  restschuld = darlehen * pow(q, monat) - annuitat * (pow(q, monat) - 1.0) / zinssatzMonatlich
  print("restschuld: " + str(restschuld))
  zins = darlehen * (pow(q, laufzeitMonaten) - pow(q, monat - 1.0)) / (pow(q, laufzeitMonaten) - 1.0) * zinssatzMonatlich
  print("zins: " + str(zins))
  tilgung = darlehen * pow(q, monat - 1.0) * zinssatzMonatlich / (pow(q, laufzeitMonaten) - 1.0)
  print("tilgung: " + str(tilgung))

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
  # immobilienEigentum.append(immobilienEigentumTotal)
  immobilienEigentum.append(immobilienEigentumTotal / (kaufpreis + nebenkosten) * 100)

print("---")
print("---")
print("zinsBezahlt: " + str(zinsBezahlt))
print("tilgungBezahlt: " + str(tilgungBezahlt))
objektTotal = eigenkapital + tilgungBezahlt
objektProzent = objektTotal / kaufpreis * 100
print("objektTotal: " + str(objektTotal))
print("objektProzent: " + str(objektProzent))
print("---")
print("---")

######################
### Visualisierung ###
######################

# Restschuld
plt.title('Restschuld')
plt.xlabel('Monate')

plt.grid(visible=True)
plt.axvline(x = zinsbindungMonate, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(monate, restschulden, label="Restschuld")
# plt.plot(monate, zinsenTotal, label="Zinsen")
plt.plot(monate, tilgungenTotal, label="Tilgung")
plt.legend()
plt.figure()

# Zins & Tilgung (monatlich)
plt.title('Zins & Tilgung (monatlich)')
plt.xlabel('Monate')

plt.grid(visible=True)
plt.ylim(0.0, annuitat * 1.1)
plt.axhline(y = annuitat, linestyle='--', color = 'g', label = 'Annuitat')
plt.plot(monate, zinsen, label="Zinsen")
plt.plot(monate, tilgungen, label="Tilgung")
plt.legend()
plt.figure()

# Immobilieneigentum
plt.title('Immobilieneigentum')
plt.xlabel('Monate')

plt.grid(visible=True)
plt.axvline(x = zinsbindungMonate, linestyle='--', color = 'r', label = 'Zinsbindung')
plt.plot(monate, immobilienEigentum, label="Eigentum %")
plt.legend()

plt.show()
