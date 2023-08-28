import re
from confluent_kafka import Producer

producer_config = {
    'bootstrap.servers': 'kafka1:19091',
    'message.timeout.ms': 1000
}
topic = "Gateway"
producer = Producer(producer_config)

def send_message(username, message):
    headers = [("username", username.encode("utf-8"))]
    producer.produce(
        topic, key="-", 
        value=message.encode("utf-8"), 
        headers=headers
    )
    producer.flush()


def get_http_headers(request):
    regex = re.compile("^HTTP_")
    result = dict(
        (regex.sub("", header), value)
        for (header, value) in request.META.items()
        if header.startswith("HTTP_")
    )

    return result

################# TOKEN VALIDATION #############################################
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import json
import requests
from datetime import datetime
from django.conf import settings
import requests

def base64url_encode(data):
    encoded = base64.urlsafe_b64encode(data)
    return encoded.rstrip(b'=').decode('utf-8')

def base64url_decode(data):
    return base64.urlsafe_b64decode(data + '=' * (4 - len(data) % 4))

def get_public_key():
    jwks_url = settings.IDENTITY_PROVIDER_JWK
    jwks_response = requests.get(jwks_url)
    jwks_data = jwks_response.json()

    n = int.from_bytes(base64url_decode(jwks_data['keys'][0]['n']), "big")
    e = int.from_bytes(base64url_decode(jwks_data['keys'][0]['e']), "big")

    public_numbers = rsa.RSAPublicNumbers(e, n)
    public_key = public_numbers.public_key(backend=default_backend())
    return public_key

def validate_jwt_signature(jwt):
    parts = jwt.split('.')
    jwt_payload = base64url_decode(parts[1])
    jwt_signature = base64url_decode(parts[2])
    public_key = get_public_key()

    public_key.verify(
        jwt_signature,
        jwt_payload,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    payload = json.loads(jwt_payload)
    
    # Check if the token is expired
    now = datetime.utcnow()
    expiration_time = datetime.utcfromtimestamp(payload.get('exp', 0))
    if expiration_time < now:
        raise ValueError()

    return payload

def authorize_request(request, admin=False):
    headers = get_http_headers(request)

    id_token = headers.get('X_ID_TOKEN', None)
    username = headers.get('X_USER_NAME')

    if id_token is None or username is None:
        return False

    try:
        jwt_payload = validate_jwt_signature(id_token)
        if admin and jwt_payload['role'] == 0:
            return False
        else:
            return jwt_payload
    except Exception as ex:
        return False

    
################################################################################