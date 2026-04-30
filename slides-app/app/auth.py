# from flask_babel import _
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_babel import _
# werkzeug.security ci offre strumenti professionali per la crittografia
from werkzeug.security import check_password_hash, generate_password_hash
from app.repositories import user_repository
from functools import wraps

# url_prefix='/auth' significa che tutte le route qui inizieranno con /auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    """
    Decoratore per proteggere le rotte.
    Se l'utente non è loggato, viene reindirizzato alla pagina di login.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # Detect AJAX/API request: check URL prefix or Accept/Content-Type header
            if request.path.startswith('/api/') or \
               request.headers.get('Content-Type') == 'application/json' or \
               request.headers.get('Accept') == 'application/json':
                from flask import jsonify
                return jsonify({
                    'ok': False,
                    'error': _('Sessione scaduta. Effettua di nuovo il login.'),
                    'redirect': url_for('auth.login')
                }), 401
            flash(_('Devi effettuare il login prima.'), 'error')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    """
    Questa funzione viene eseguita AUTOMATICAMENTE prima di ogni richiesta.
    Serve a caricare l'utente dal DB e renderlo disponibile in tutto il sito.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Carichiamo l'utente e lo mettiamo in g.user
        # Ora g.user sarà disponibile anche nei template HTML!
        g.user = user_repository.get_user_by_id(user_id)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Registrazione di un nuovo utente."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email'].strip()
        error = None

        if not username:
            error = _('Username obbligatorio.')
        elif not password:
            error = _('Password obbligatoria.')
        elif not email:
            error = _('Email obbligatoria.')
        elif '@' not in email or '.' not in email:
            error = _('Inserisci un indirizzo email valido.')

        if error is None:
            # Hashiamo la password (MAI salvarla in chiaro!)
            hashed_pwd = generate_password_hash(password)
            try:
                user_repository.create_user(username, hashed_pwd, email)
                flash(_('Registrazione riuscita! Ora puoi fare login.'), 'success')
                return redirect(url_for('auth.login'))
            except ValueError as e:
                error = str(e)
        
        if error:
            flash(_(error), 'error')

    # CASO 1: GET (Mostriamo il form)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Login di un utente."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = user_repository.get_user_by_username(username)

        if user is None:
            error = _('Username non corretto.')
        # 2. Verifichiamo la password
        elif not check_password_hash(user['password'], password):
            error = _('Password non corretta.')

        if error is None:
            # 3. GESTIONE SESSIONE (Mettiamo il "braccialetto")
            # Preserviamo la lingua prima di cancellare la sessione
            lang = session.get('lang', 'it')
            # Puliamo eventuali vecchie sessioni
            session.clear()
            # Salviamo l'ID dell'utente nel cookie di sessione
            session['user_id'] = user['id']
            # Ripristiniamo la lingua scelta
            session['lang'] = lang
            
            # Ora il browser ricorderà chi siamo!
            flash(_('Benvenuto {username}!').format(username=user["username"]), 'success')
            return redirect(url_for('presentations.list_presentations'))

        if error:
            flash(error, 'error')

    # CASO 1: GET (Mostriamo il form)
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    # Per uscire, "tagliamo il braccialetto"
    # Preserviamo la lingua prima di cancellare la sessione
    lang = session.get('lang', 'it')
    session.clear()
    # Ripristiniamo la lingua scelta
    session['lang'] = lang
    flash(_('Logout effettuato. Arrivederci!'), 'success')
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/forgot-password', methods=('GET', 'POST'))
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = user_repository.get_user_by_email(email)
        # Sempre mostrare il messaggio generico per sicurezza
        flash(_('Se l\'email è registrata, riceverai un link per il reset.'), 'success')
        if user:
            import secrets
            from datetime import datetime, timedelta
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
            user_repository.save_reset_token(user['id'], token, expires_at)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            # Per test in sviluppo: stampiamo il link in console
            # In produzione, inviare email reale con Flask-Mail
            current_app.logger.info(f'Password reset link: {reset_url}')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')


@bp.route('/reset-password/<token>', methods=('GET', 'POST'))
def reset_password(token):
    token_row = user_repository.get_valid_reset_token(token)
    if not token_row:
        flash(_('Link non valido o scaduto.'), 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if not password:
            flash(_('Password obbligatoria.'), 'error')
        elif password != confirm:
            flash(_('Le password non coincidono.'), 'error')
        else:
            user_repository.update_password(token_row['user_id'], generate_password_hash(password))
            user_repository.mark_reset_token_used(token_row['id'])
            flash(_('Password reimpostata con successo. Ora puoi fare login.'), 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

