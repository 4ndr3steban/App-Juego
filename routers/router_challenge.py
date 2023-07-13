### Challenge API ###

from fastapi import APIRouter, HTTPException, status
from .models.microchallenge import microChallenge
from .models.macrochallenge import macroChallenge
from .models.user import User
from settings import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials

router = APIRouter(prefix="/challenges",
                    tags=["challenge"],
                    responses={status.HTTP_404_NOT_FOUND: {"response": "not found"}})


# DATABASE -------------------------------

credentials = {"type": settings.type,
    "project_id": settings.project_id,
    "private_key_id": settings.private_key_id,
    "private_key": settings.private_key,
    "client_email": settings.client_email,
    "client_id": settings.client_id,
    "auth_uri": settings.auth_uri,
    "token_uri": settings.token_uri,
    "auth_provider_x509_cert_url": settings.auth_provider_x509_cert_url,
    "client_x509_cert_url": settings.client_x509_cert_url,
    "universe_domain": settings.universe_domain}


gc = gspread.service_account_from_dict(credentials)

gsheet = gc.open("database")

wsheet = gsheet.worksheet("usuarios")
miccsheet = gsheet.worksheet("microchallenges")
maccsheet = gsheet.worksheet("macrochallenges")


# ---------------------------------------------------------


# RUTAS --------------------------------------------------- 

@router.get("/{email}/macro", response_model = dict, status_code = status.HTTP_200_OK)
async def macrochallenges(email: str):
    """ Obtener los macrochallenges para un usuario

    -input: email
    -output: dict

    Se obtienen los macrochallenges filtrando los que el usuario
    ya ha realizado
    """

    # Se busca el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    # Se obtienen los challenges de la db
    challenges = search_macrochallenges()

    # Se obtienen los challenges del historial del usuario y sus titulos
    challHist = user.challengeHistory
    titles = [challenge[0] for challenge in challHist]

    # Se filtran los challenges que esten en los titulos del historial
    for chall in challenges:
        if chall.name in titles:
            chall.completed = True

    return {"challenges": challenges}


@router.get("/{email}/micro", response_model = dict, status_code = status.HTTP_200_OK)
async def microchallenges(email: str):
    """ Obtener los challenges para un usuario

    -input: email
    -output: dict

    Se obtienen los challenges filtrando los que el usuario
    ya ha realizado (se obtienen los challenges No realizados)
    """

    # Se busca el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    # Se obtienen los challenges de la db
    challenges = search_microchallenges()

    # Se obtienen los challenges del historial del usuario y sus titulos
    challHist = user.challengeHistory
    titles = [challenge[0] for challenge in challHist]

    # Se filtran los challenges que esten en los titulos del historial
    for chall in challenges:
        if chall.name in titles:
            chall.completed = True

    return {"challenges": challenges}

# ---------------------------------------------------------

# HELPERS --------------------------------------------------------

def search_user(email: str):
    """ Buscar un usuario en la base de datos

    -input: email
    -output: usuario

    Se busca el usuario en la base de datos segun su email
    y se obtienen todos sus datos:
    (email, points, redeemHistory, challengeHistory, badges)
    """

    # Obtener todos los datos
    list_of_dicts = wsheet.get_all_records()

    # Filtrar el usuario buscado
    list_users = list(filter(lambda user: user["email"] == email, list_of_dicts))
    try:
        # Obtener cada datos

        l1 = list_users[0]["email"]
        l2 = int(list_users[0]["points"])

        l3 = list_users[0]["redeemHistory"].split(", ")
        l3 = [(l3[i], int(l3[i+1])) for i in range(0, len(l3)-1, 2)]

        l4 = list_users[0]["challengeHistory"].split(", ")
        l4 = [(l4[i], int(l4[i+1])) for i in range(0, len(l4)-1, 2)]

        l5 = list(map(int, list_users[0]["badges"].split(", ")))

        # Instanciar el usuario
        user = User(email=l1,points=l2, redeemHistory=l3, challengeHistory=l4, badges=l5)

        return user
    
    except Exception:
        # Error si no encuentra el usuario
        return {"message": "user not found"}
    

def search_macrochallenges():
    """ Obtener los macrochallenges de la db

    -input: 
    -output: list

    Se buscan y guardan en una lista todos los
    macrochallenges de la db
    """

    # Se obtienen todos los datos de la hoja
    list_of_mac = maccsheet.get_all_records()

    # Lista para guardar los challenges
    list_challenges = []

    # Recorrer cada dato de la hoja
    for mac in list_of_mac:

        # Obtener cada dato
        l1 = mac["id"]
        l2 = mac["category"]
        l3 = int(mac["points"])
        l4 = mac["completed"]
        l5 = mac["name"]
        l6 = mac["image"]
        l7 = mac["bg_color"]
        l8 = mac["time"]
        l9 = mac["forms"]

        # Instanciar el challenge y agregarlo a la lista
        challenge = macroChallenge(id= l1, category= l2, points= l3, completed= l4, name= l5, image= l6, bg_color= l7, time= l8, forms= l9)
        list_challenges.append(challenge)

    return list_challenges
    

def search_microchallenges():
    """ Obtener los microchallenges de la db

    -input: 
    -output: list

    Se buscan y guardan en una lista todos los
    microchallenges de la db
    """

    # Se obtienen todos los datos de la hoja
    list_of_mic = miccsheet.get_all_records()

    # Lista para guardar los challenges
    list_challenges = []

    # Recorrer la lista de microchallenges
    for mic in list_of_mic:

        # Obtener cada dato
        l1 = mic["id"]
        l2 = mic["category"]
        l3 = int(mic["points"])
        l4 = mic["completed"]
        l5 = mic["name"]
        l6 = mic["icon"]
        l7 = mic["bg_color"]

        # Instanciar el challenge y agregarlo a la lista
        challenge = microChallenge(id= l1, category= l2, points= l3, completed= l4, name= l5, icon= l6, bg_color= l7)
        list_challenges.append(challenge)

    return list_challenges

def search_row(email: str):
    """ Buscar la fila en la cual se encuentra un usuario

    -input: email
    -output: int

    Busca el indice de la columna en la que estan
    los datos de un usuario
    """

    values_list = wsheet.col_values(1)

    return values_list.index(email)

    
# ----------------------------------------------------------------