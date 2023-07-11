from dotenv import load_dotenv
import os
from dataclasses import dataclass

#Configuracion de las variables de entorno
@dataclass
class Settings:
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str

# Cargar variables de entorno
load_dotenv()

#Guardar variables de entorno
settings = Settings(type=os.getenv("type"),
                    project_id=os.getenv("project_id"),
                    private_key_id=os.getenv("private_key_id"),
                    private_key=os.getenv("private_key"),
                    client_email=os.getenv("client_email"),
                    client_id=os.getenv("client_id"),
                    auth_uri=os.getenv("auth_uri"),
                    token_uri=os.getenv("token_uri"),
                    auth_provider_x509_cert_url=os.getenv("auth_provider_x509_cert_url"),
                    client_x509_cert_url=os.getenv("client_x509_cert_url"),
                    universe_domain=os.getenv("universe_domain"))