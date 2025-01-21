from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
import os

translations = {
    'en': {
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'exam_lobby': 'Exam lobby',
        'stop_exam': 'Stop',
        'exam_results': 'Results',
        'edit_exam': 'Edit',
        'delete_exam': 'Delete',
        'create_exam': 'Create new exam',
        'enter_exam_name': 'Enter exam name',
        'save_exam_name': 'Save exam name',
        'add_question': 'Add question',
        'question_text': 'Question text',
        'option_a': 'Option a)',
        'option_b': 'Option b)',
        'option_c': 'Option c)',
        'option_d': 'Option d)',
        'correct_answer': 'Correct answer',
        'points': 'Points',
        'save_question': 'Save question',
        'edit_question': 'Edit question',
        'save_changes': 'Save changes',
        'participants': 'Participants',
        'start_exam': 'Start exam',
        'results': 'Results',
        'reset_exam': 'Reset exam',
        'enter_exam_code': 'Enter exam code',
        'join_exam': 'Join exam',
        'scoreboard': 'Scoreboard',
        'stop_exam': 'Stop exam',
        'start_message': 'Professor will start the exam soon',
        'wait_message': 'Please wait on this page',
        'login': 'Login',
        'close': 'Close',
        'password': 'Password',
        'no_account': 'Don\'t have an account? Register here',
        'register': 'Register',
        'first_name': 'First name',
        'last_name': 'Last name',
        'student': 'Student',
        'professor': 'Professor',
        'have_account': 'Already have an account? Login here',
        'answered_all_questions': 'You\'ve answered all question. Please wait for the final results.',
        'exam_stopped': 'The exam has been stopped by professor. Please wait for the final results.',
        'exam_reset': 'The exam has been reset. Please re-join the exam with the same code.'
    },
    'hr': {
        'dashboard': 'Nadzorna ploča',
        'logout': 'Odjava',
        'exam_lobby': 'Čekaonica',
        'stop_exam': 'Zaustavi',
        'exam_results':'Rezultati',
        'edit_exam': 'Uredi',
        'delete_exam': 'Izbriši',
        'create_exam': 'Stvori novi ispit',
        'enter_exam_name': 'Unesi naziv ispita',
        'save_exam_name': 'Spremi naziv ispita',
        'add_question': 'Unos pitanja',
        'question_text': 'Tekst pitanja',
        'option_a': 'Opcija a)',
        'option_b': 'Opcija b)',
        'option_c': 'Opcija c)',
        'option_d': 'Opcija d)',
        'correct_answer': 'Točan odgovor',
        'points': 'Bodovi',
        'save_question': 'Spremi pitanje',
        'edit_question': 'Uredi pitanje',
        'save_changes': 'Spremi promjene',
        'participants': 'Sudionici',
        'start_exam': 'Pokreni ispit',
        'results': 'Rezultati',
        'reset_exam': 'Resetiraj ispit',
        'enter_exam_code': 'Unesi kod ispita',
        'join_exam': 'Pridruži se ispitu',
        'scoreboard': 'Rang lista',
        'stop_exam': 'Zaustavi ispit',
        'start_message': 'Nastavnik će ubrzo pokrenuti ispit',
        'wait_message': 'Molimo pričekajte na ovoj stranici',
        'login': 'Prijava',
        'close': 'Zatvori',
        'password': 'Lozinka',
        'no_account': 'Nemate korisnički račun? Registrirajte se ovdje',
        'register': 'Registracija',
        'first_name': 'Ime',
        'last_name': 'Prezime',
        'student': 'Učenik',
        'professor': 'Nastavnik',
        'have_account': 'Već imate korisnički račun? Prijavite se ovdje',
        'answered_all_questions': 'Odgovorili ste na sva pitanja. Molim pričekajte konačne rezultate.',
        'exam_stopped': 'Nastavnik je zaustavio ispit. Molim pričekajte konačne rezultate.',
        'exam_reset': 'Nastavnik je resetirao ispit. Molim ponovno se pridružite ispitu s istim kodom.'
    }
}

def get_translation(key):
    lang = session.get('lang', 'en') #default is en
    return translations.get(lang, {}).get(key, key)

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')  

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    from .models import User, Exam, Question, Score

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'main.login'

    @app.context_processor
    def inject_translation():
        return dict(get_translation=get_translation)

    return app
