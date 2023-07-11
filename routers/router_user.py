### Users API ###

from fastapi import APIRouter, HTTPException, status
from .models.user import User
from .models.product import Product
from .models.challenge import Challenge
from settings import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials


router = APIRouter(prefix="/user",
                    tags=["user"],
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

# Iniciar servicio
gc = gspread.service_account_from_dict(credentials)

# Abrir sheet
gsheet = gc.open("database")

# Abrir hojas
wsheet = gsheet.worksheet("usuarios")
csheet = gsheet.worksheet("challenges")
psheet = gsheet.worksheet("products")

# ---------------------------------------------------------

# RUTAS --------------------------------------------------- 

@router.get("/{email}", response_model = User, status_code = status.HTTP_200_OK)
async def user(email: str):
    """Retornar un usuario segun su email

    - input: email
    - output: usuario
    Se busca el usuario en la db, se retorna un error
    si el usuario no se encuentra
    """

    # Buscar el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    return user

@router.post("/{email}/adduser", response_model = dict, status_code = status.HTTP_200_OK)
async def adduser(email: str):
    """ Agregar usuario a la db

    -input: email
    -output: dict

    Mirar si el usuario existe para manejo de error,
    si no existe, se agrega a la db con los datos en 0
    """

    # Buscar el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) == User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="existed user")
    
    # Setear el usuario con los datos en 0
    wsheet.update(f'A{len(wsheet.col_values(1))+1}:E{len(wsheet.col_values(1))+1}', [[email, 0, "","", "0, 0, 0, 0"]])

    return {"added": [email, 0, "","", "0, 0, 0, 0"]}


@router.get("/{email}/infouser", response_model= dict, status_code = status.HTTP_200_OK)
async def infouser(email: str):
    """ Obtener la informacion de un usuario

    -input: email
    -output: dict

    Se buscan y obtienen los datos del historial de un usuario
    """

    # Se busca el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    # Puntos de todos los usuarios
    points = list(map(int, wsheet.col_values(2)[1:]))

    # Puntos del usuario a buscar
    p = user.points

    # Variable de control
    next = 10000000

    # Buscar lo que le falta al usuario para subir de nivel en el ranking
    if p == max(points):
        nextlev = {"nextLevel": 0}
    else:
        for i in points:
            if p < i < next:
                next = i

        nextlev = {"nextLevel": next-p}

    # Retos completos
    completed = len(user.challengeHistory)

    # Recompensas reclamadas
    earned = len(user.redeemHistory)

    # Insigneas
    badg_lst = [False for _ in range(len(user.badges))]

    # Se setea en badg_lst las insigneas que se deben activar
    for idx in range(len(user.badges)):
        if user.badges[idx] >= 5:
            badg_lst[idx] = True

    # Insigneas seteadas
    badgs = {"water": badg_lst[0], "air": badg_lst[1], "land": badg_lst[2], "fire": badg_lst[3]}

    # Variable a retornar
    ans = {"points": user.points,
           "nextLevel": nextlev["nextLevel"],
           "completed": completed,
           "earned": earned,
           "badges": badgs}

    return ans


@router.post("/{email}/addproduct", response_model= dict, status_code = status.HTTP_200_OK)
async def addchallenge(email: str, product: Product):
    """ Agregar una nueva recompensa reclamada al historial

    -input: email
    -output: dict

    Se agrega una recompensa reclamada al historial de un usuario
    y se restan los puntos correspondientes
    """

    # Buscar el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    # Buscar las recompensas en la db
    products_list = search_products()
    names = [prod.name for prod in products_list]

    if product.name not in names:
        # Error si la recompensa ingresada no existe en la db
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="challenge not found")


    if user.points - product.cost < 0:
        # Manejo de error si los puntos son insuficientes
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED, detail="insufficient points")
    else:

        # Agregar la recompensa al historial
        prodHist = user.redeemHistory
        prodHist.append([product.name, product.cost])

        anshist = ""

        # Escribir el nuevo historial en la db como string
        for prod in prodHist:
            anshist += prod[0] + ", " + str(prod[1]) + ", "

        wsheet.update_cell(search_row(user.email)+1, 3, anshist[:-2])

        # Restar los puntos en la db
        wsheet.update_cell(search_row(user.email)+1, 2, user.points - product.cost)
            
        return {"message": "successfull"}
    

@router.post("/{email}/addchallenge", response_model= dict, status_code = status.HTTP_200_OK)
async def addchallenge(email: str, challenge: Challenge):
    """ Agregar un nuevo reto cumplido al historial de un usuario

    -input: email
    -output: dict

    Se agrega un reto cumplido al historial, se suman los puntos,
    se actualizan las insigneas y devolver el forms correspondiente
    """

    # Buscar al usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    

    # Obetener los titulos de los challenges de la db
    challenges_list = search_challenges()
    titles = [challenge.title for challenge in challenges_list]

    if challenge.title not in titles:
        # Error si el challenge ingresado no existe en la db
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="challenge not found")


    # Obtener el historial y agregar el nuevo reto
    challHist = user.challengeHistory
    challHist.append([challenge.title, challenge.points])

    anshist = ""

    # Escribir el nuevo historial en la db como string
    for chall in challHist:
        anshist += chall[0] + ", " + str(chall[1]) + ", "

    wsheet.update_cell(search_row(user.email)+1, 4, anshist[:-2])

    # Sumar los puntos
    wsheet.update_cell(search_row(user.email)+1, 2, user.points + challenge.points)

    # Obtener las insigneas y sumar 1 a la correspondiente
    badges_cat = ["water", "air", "land", "fire"]
    badges = user.badges
    badges[badges_cat.index(challenge.cluster)] += 1

    ansbadg = ""

    # Escribir las nuevas insigneas en la db como string
    for badg in badges:
        ansbadg += str(badg) + ", "

    wsheet.update_cell(search_row(user.email)+1, 5, ansbadg[:-2])
        
    return {"urlForms": challenge.form}


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


def search_challenges():
    """ Obtener los challenges de la db

    -input: 
    -output: list

    Se buscan y guardan en una lista todos los
    challenges de la db
    """

    # Se obtienen todos los datos de la hoja
    list_of_dicts = csheet.get_all_records()

    # Lista para guardar los challenges
    list_challenges = []

    # Recorrer cada dato de la hoja
    for chall in list_of_dicts:

        # Obtener cada dato 
        l1 = chall["title"]
        l2 = chall["cluster"]
        l3 = int(chall["points"])
        l4 = chall["image"]

        l5 = chall["ismacro"]
        if l5 == "true":
            l5 = True
        else:
            l5 = False

        l6 = int(chall["exp_time"])
        l7 = chall["form"]

        # Instanciar el challenge y agregarlo a la lista
        challenge = Challenge(title=l1, cluster=l2, points=l3, image=l4, ismacro=l5, exp_time=l5, form=l7)
        list_challenges.append(challenge)

    return list_challenges


def search_products():
    """ Obtener los productos (recompensas) de la db

    -input: 
    -output: list

    Se buscan y guardan en una lista todos los
    productos de la db
    """

    # Se obtienen todos los datos de la hoja
    list_of_dicts = psheet.get_all_records()

    # Lista para guardar los productos
    list_products = []

    # Recorrer cada dato de la hoja
    for prod in list_of_dicts:
        # Obtener cada dato
        l1 = prod["name"]
        l2 = int(prod["cost"])
        l3 = prod["category"]
        l4 = prod["image"]

        # Instanciar el producto y agregarlo a la lista
        product = Product(name= l1, cost= l2, category= l3, img= l4)
        list_products.append(product)

    return list_products


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