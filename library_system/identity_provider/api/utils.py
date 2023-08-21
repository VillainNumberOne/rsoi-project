import hashlib
from django.db import connection
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import time
import json
import requests
from datetime import datetime

IDENTITY_PROVIDER_URL = "http://localhost:8000/api/v1/.well-known/jwks.json"

def custom_authenticate(username, password):
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, user_uid, username, password_hash, user_role FROM users WHERE username = %s AND password_hash = %s",
            [username, password_hash]
        )
        user_row = cursor.fetchone()

    if user_row:
        user_dict = {
            'id': user_row[0],
            'uid': str(user_row[1]),
            'username': user_row[2],
            'role': user_row[4],
        }
        return user_dict

    return None

def create_new_user(username, password):
    user_uid = uuid.uuid4() 
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    role = 0

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE username = %s", [username])
        existing_user_id = cursor.fetchone()

    if existing_user_id:
        return None

    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (user_uid, username, password_hash, user_role) VALUES (%s, %s, %s, %s) RETURNING id",
            [user_uid, username, password_hash, role]
        )
        new_user_id = cursor.fetchone()[0]

    user_dict = {
        'id': new_user_id,
        'uid': str(user_uid),
        'username': username,
        'role': role
    }

    return user_dict

def load_private_key(private_key_file_path='private_key.pem'):
    with open(private_key_file_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def generate_private_key(private_key_file_path='private_key.pem'):
    try:
        private_key = load_private_key(private_key_file_path)
    except FileNotFoundError:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        with open(private_key_file_path, 'wb') as key_file:
            key_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

    return private_key

def build_jwk():
    private_key = generate_private_key()
    public_key = private_key.public_key()

    n = public_key.public_numbers().n
    e = public_key.public_numbers().e

    jwk = {
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "kid": "1", 
        "n": base64url_encode(n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')),
        "e": base64url_encode(e.to_bytes((e.bit_length() + 7) // 8, byteorder='big'))
    }

    return jwk

def base64url_encode(data):
    encoded = base64.urlsafe_b64encode(data)
    return encoded.rstrip(b'=').decode('utf-8')

def base64url_decode(data):
    return base64.urlsafe_b64decode(data + '=' * (4 - len(data) % 4))

def sign_jwt(payload, private_key):
    payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    signature = private_key.sign(
        payload_bytes,
            padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    jwt = '{}.{}.{}'.format(
        base64url_encode(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode('utf-8')),
        base64url_encode(payload_bytes),
        base64url_encode(signature)
    )

    return jwt

def generate_id_token(user):
    private_key = generate_private_key()
    id_token_payload = {
        'iss': 'RSOI Identity Provider',  
        'sub': user['id'],            
        'aud': 'Library System',           
        'exp': int(time.time()) + 3600, # 1 hour
        'iat': int(time.time()),
        'uid': user['uid'],
        'username': user['username'],
        'role': user['role']            
    }

    id_token = sign_jwt(id_token_payload, private_key)

    return id_token

def generate_refresh_token(user):
    private_key = generate_private_key()
    refresh_token_payload = {
        'sub': str(user['id']),
        'exp': int(time.time()) + 604800,  # 7 days
        'iat': int(time.time())
    }
    refresh_token = sign_jwt(refresh_token_payload, private_key)

    return refresh_token

def get_public_key():
    jwks_url = IDENTITY_PROVIDER_URL
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
