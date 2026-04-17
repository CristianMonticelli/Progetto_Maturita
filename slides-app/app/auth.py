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
        error = None

        if not username:
            error = _('Username obbligatorio.')
        elif not password:
            error = _('Password obbligatoria.')

        if error is None:
            # Hashiamo la password (MAI salvarla in chiaro!)
            hashed_pwd = generate_password_hash(password)
            try:
                user_repository.create_user(username, hashed_pwd)
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
            # Puliamo eventuali vecchie sessioni
            session.clear()
            # Salviamo l'ID dell'utente nel cookie di sessione
            session['user_id'] = user['id']
            
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
    session.clear()
    flash(_('Logout effettuato. Arrivederci!'), 'success')
    return redirect(url_for('presentations.list_presentations'))

