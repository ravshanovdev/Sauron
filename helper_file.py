import jwt
import datetime
import secrets
from functools import wraps

# just for test
SECRET_KEY = "f3b8d966690de4d40b1f843216f2998ac66cbb2dff09b5717d25e617370deda5"


def generate_token(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def auth_required(f):
    @wraps(f)
    def decorated(req, resp, *args, **kwargs):
        auth_header = req.headers.get("Authorization")

        def reject(msg):
            resp.status_code = 401
            resp.json = {"error": msg}
            return

        if not auth_header or not auth_header.startswith("Bearer "):
            return reject("Token Required!")

        try:
            token = auth_header.split("Bearer ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            req.user_id = payload.get("user_id")
            req.username = payload.get("username")
        except (IndexError, AttributeError):
            return reject("Incorrect Token!")
        except jwt.ExpiredSignatureError:
            return reject("Token Expired!")
        except jwt.InvalidTokenError:
            return reject("Invalid Token")

        return f(req, resp, *args, **kwargs)

    return decorated

