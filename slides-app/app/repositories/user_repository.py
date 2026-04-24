# MFA/OTP/Email support
def update_mfa(user_id, mfa_enabled, mfa_secret=None):
    """Enable or disable MFA for a user. mfa_enabled: 0=off, 1=TOTP, 2=email"""
    db = get_db()
    db.execute(
        'UPDATE user SET mfa_enabled=?, mfa_secret=? WHERE id=?',
        (mfa_enabled, mfa_secret, user_id)
    )
    db.commit()

def update_email(user_id, email):
    db = get_db()
    db.execute('UPDATE user SET email=? WHERE id=?', (email, user_id))
    db.commit()

def save_otp_token(user_id, token, expires_at):
    """Save a new OTP token, invalidating all previous ones for this user."""
    db = get_db()
    db.execute('DELETE FROM otp_tokens WHERE user_id=?', (user_id,))
    db.execute(
        'INSERT INTO otp_tokens (user_id, token, expires_at) VALUES (?,?,?)',
        (user_id, token, expires_at)
    )
    db.commit()

def get_valid_otp_token(user_id, token):
    """Return the token row if it exists, is not used, and is not expired."""
    from datetime import datetime
    db = get_db()
    row = db.execute(
        'SELECT * FROM otp_tokens WHERE user_id=? AND token=? AND used=0',
        (user_id, token)
    ).fetchone()
    if row and datetime.fromisoformat(row['expires_at']) > datetime.now():
        return dict(row)
    return None

def mark_otp_used(token_id):
    db = get_db()
    db.execute('UPDATE otp_tokens SET used=1 WHERE id=?', (token_id,))
    db.commit()
# Importiamo la nostra funzione per prendere la connessione
from app.db import get_db

def create_user(username, password_hash, email=None):
    """Inserisce un nuovo utente."""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
            (username, password_hash, email),
        )
        db.commit()  # Salviamo le modifiche
        return True
    except db.IntegrityError:
        # Errore: lo username esiste già
        raise ValueError(f"L'utente {username} è già registrato.")

def authenticate_user(username, password):
    """Autentica un utente."""
    from werkzeug.security import check_password_hash
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def get_user_by_email(email):
    """Restituisce un utente cercandolo per email."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE email = ?", (email,)
    ).fetchone()
    return dict(user) if user else None

def get_user_by_username(username):
    """Cerca un utente per nome."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()
    return user

def get_user_by_id(user_id):
    """Cerca un utente per ID."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE id = ?", (user_id,)
    ).fetchone()
    return user
