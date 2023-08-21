import re
import jwt
from jwt import PyJWKClient


def get_http_headers(request):
    regex = re.compile("^HTTP_")
    result = dict(
        (regex.sub("", header), value)
        for (header, value) in request.META.items()
        if header.startswith("HTTP_")
    )

    return result


def get_token(request):
    headers = get_http_headers(request)
    if "AUTHORIZATION" in headers.keys():
        token = headers["AUTHORIZATION"]
    else:
        token = None
    return token


def get_username(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    if 'sub' in payload:
        return payload['sub']
    else:
        return None


def verify(request):
    token = get_token(request)
    if token is None:
        return False

    jwk_url = "https://dev-72954585.okta.com/oauth2/default/v1/keys"
    try:
        jwks_client = PyJWKClient(jwk_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="api://default")
    except Exception:
        return False
    else:
        return True
