# Programoje naudojamu konstantu failas

# Langu pavadinimu zymejimai, naudojama pakeisti rodomaji langa vartotojui
WINDOW_HOME = "HOME"
WINDOW_LOGIN = "LOGIN"

# Langu antrasciu pavadinimai (title)
BASE_TITLE = "Bilietai"
TITLE_HOME = BASE_TITLE
TITLE_LOGIN = BASE_TITLE + " - " + "prisijungimas"

# Minimalus lango dydis
MIN_WIDTH = 640
MIN_HEIGHT = 480

# Spalvos kedziu statusui
SPALVA_NEPASIRINKTA = 'green'
SPALVA_UZIMTA = 'red'
SPALVA_GEDIMAS = 'dark slate gray'  # Kai negalima parduoti vietos (suluzus ar pns.)
SPALVA_PASIRINKTA = 'yellow'
SPALVA_KATIK_NUPIRKTA = 'orange'
SPALVA_LAIPTAI = 'light grey'

# Vietu reiksmiu statusas duomenu bazeje ir, kaip reaguoti i pasirinktos vietos paspaudima keiciant vietos statusa
REIKSME_LAIPTAI = 0
REIKSME_LAISVA = 1
REIKSME_UZIMTA = 2
REIKSME_GEDIMAS = 3
REIKSME_PASIRINKTA = "P"
REIKSME_NEPASIRINKTA = "NE"
REIKSME_KATIK_NUSIPIRKO = "KN"


# Vartotojo pasisvekinimo zinute
def welcomeMessage(name=""):
    return "Sveiki, {}!".format(name)


DEFAULT_ACTIONS_LABEL_MESSAGE = "Sveiki atvyke!"

WELCOME_MESSAGE_NOT_LOGGED = "Jus esate neprisijunges!"
