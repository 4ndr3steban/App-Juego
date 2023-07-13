### Products API ###

from fastapi import APIRouter, HTTPException, status
from .models.product import Product
from .models.user import User
from settings import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials

router = APIRouter(prefix="/products",
                   tags=["products"],
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
psheet = gsheet.worksheet("products")


# ---------------------------------------------------------


# RUTAS --------------------------------------------------- 

@router.get("/{email}", response_model = dict, status_code = status.HTTP_200_OK)
async def products(email: str):
    """ Obtener los productos (recompensas) para un usuario

    -input: email
    -output: dict
    """

    # Obtener el usuario
    user = search_user(email)

    # Manejo de error
    if type(user) != User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    # Se obtiene la lista de productos de la db
    products_list = search_products()

    return {"products": products_list}

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
        l1 = prod["id"]
        l2 = prod["name"]
        l3 = int(prod["cost"])
        l4 = prod["category"]
        l5 = prod["image"]

        # Instanciar el producto y agregarlo a la lista
        product = Product(id= l1, name= l2, cost= l3, category= l4, img= l5)
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