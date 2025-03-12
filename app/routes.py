from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Exam, Question, Score  
from .__init__ import translations
from .forms import LoginForm, RegistrationForm
from . import db, socketio
from flask_socketio import emit, join_room, leave_room
from werkzeug.security import check_password_hash

bp = Blueprint('main', __name__)
exam_participants = {}
LANGUAGES = {
    'en': 'English',
    'hr': 'Croatian'
}

@bp.route('/set_language/<language>')
def set_language(language):
    if language not in LANGUAGES.keys():
        language = 'en' 
    session['lang'] = language
    return redirect(request.referrer)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'professor':
            return redirect(url_for('main.professor_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('main.join_exam'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not check_password_hash(user.password_hash, form.password.data):
            flash('Email or password is not valid.', 'danger')
        else:
            login_user(user)
            return redirect(url_for('main.index'))  

    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def professor_dashboard():
    exams = Exam.query.filter_by(created_by=current_user.id).all()
    return render_template('dashboard.html', exams=exams)

@bp.route('/create_exam', methods=['GET', 'POST'])
@login_required
def create_exam():
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        exam = Exam(name=exam_name, created_by=current_user.id)
        db.session.add(exam)
        db.session.commit()
        return redirect(url_for('main.exam_data', exam_id=exam.id))
    return render_template('create_exam.html')

@bp.route('/exam_data/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def exam_data(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        points = request.form['points']  

        question = Question(
            exam_id=exam_id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            points=points
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.exam_data', exam_id=exam.id))
    
    questions = Question.query.filter_by(exam_id=exam.id).all()
    return render_template('exam_data.html', exam=exam, questions=questions)

@bp.route('/edit_exam_name/<int:exam_id>', methods=['POST'])
@login_required
def edit_exam_name(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if exam.created_by != current_user.id:
        return jsonify(success=False), 403
    
    new_name = request.json.get('name')
    if new_name:
        exam.name = new_name
        db.session.commit()
        return jsonify(success=True)
    
    return jsonify(success=False), 400

@bp.route('/delete_exam/<int:exam_id>', methods=['POST'])
@login_required
def delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    try:
        # Delete all associated questions
        Question.query.filter_by(exam_id=exam.id).delete()
        db.session.delete(exam)
        db.session.commit()
        flash('Exam deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting exam: {str(e)}', 'danger')
    return redirect(url_for('main.professor_dashboard'))

@bp.route('/join_exam', methods=['GET', 'POST'])
@login_required
def join_exam():
    if request.method == 'POST':
        exam_code = request.form['exam_code']
        exam = Exam.query.filter_by(code=exam_code).first()
        if exam:
            session['exam_id'] = exam.id
            exam_participants.setdefault(exam.id, []).append(current_user.id)

            # Emit the event to update other participants on the server-side
            socketio.emit('student_joined', {
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'student_count': len(exam_participants[exam.id])  
            }, room=exam.code)

            return render_template('loading_exam.html', exam=exam)
        else:
            flash('Invalid exam code.', 'danger')
            return redirect(url_for('main.join_exam'))
    return render_template('join_exam.html')

@bp.route('/exam_lobby/<int:exam_id>')
@login_required
def exam_lobby(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    students = User.query.filter(User.id.in_(exam_participants.get(exam_id, []))).all()
    return render_template('exam_lobby.html', students=students, exam=exam)

@bp.route('/start_exam/<int:exam_id>', methods=['POST'])
@login_required
def start_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    exam.active = 'started'
    db.session.commit()

    socketio.emit('exam_started', {
        'role': 'student',
        'redirect_url': url_for('main.take_exam', exam_id=exam.id, _external=True),  
        'exam_id': exam.id
    }, room=exam.code)

    return jsonify(success=True, redirect_url=url_for('main.live_scoreboard', exam_id=exam.id, _external=True))

@bp.route('/get_question/<int:exam_id>/<int:question_index>')
@login_required
def get_question(exam_id, question_index):
    exam = Exam.query.get_or_404(exam_id)
    question = Question.query.filter_by(exam_id=exam_id).order_by(Question.id).offset(question_index).first_or_404()
    
    return jsonify({
        'id': question.id,
        'question_text': question.question_text,
        'option_a': question.option_a,
        'option_b': question.option_b,
        'option_c': question.option_c,
        'option_d': question.option_d,
    })

@bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.question_text = request.form['question_text']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_answer = request.form['correct_answer']
        question.points = request.form['points']
        db.session.commit()
        flash('Question updated successfully', 'success')
        return redirect(url_for('main.exam_data', exam_id=question.exam_id))
    return render_template('edit_question.html', question=question)

@bp.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    exam_id = question.exam_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully', 'success')
    return redirect(url_for('main.exam_data', exam_id=exam_id))

@bp.route('/take_exam/<int:exam_id>')
@login_required
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    questions = Question.query.filter_by(exam_id=exam.id).all()

    questions_data = [
        {
            'id': question.id,
            'question_text': question.question_text,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
        }
        for question in questions
    ]

    return render_template('take_exam.html', exam=exam, questions=questions_data)

@bp.route('/submit_answer/<int:question_id>', methods=['POST'])
@login_required
def submit_answer(question_id):
    question = Question.query.get_or_404(question_id)
    answer = request.json['answer']
    correct = (answer == question.correct_answer)

    exam_code = question.exam.code 
    
    if correct:
        points = question.points
        Score.update_score(exam_id=question.exam_id, student_id=current_user.id, points=points)
        
        # Emit the score update event
        print(f"[DEBUG] Emitting score_update event for Student {current_user.id} in Exam {question.exam_id}, Exam Code: {exam_code}")
        socketio.emit('score_update', {
            'student_id': current_user.id,
            'exam_code': exam_code
        }, room=exam_code)

    return jsonify(success=True)

@bp.route('/get_scores/<string:exam_code>', methods=['GET'])
@login_required
def get_scores(exam_code):
    exam = Exam.query.filter_by(code=exam_code).first_or_404()
    scores = Score.query.filter_by(exam_id=exam.id).all()

    score_data = []
    for score in scores:
        student = User.query.get(score.student_id)
        score_data.append({
            'student_id': score.student_id,
            'student_name': f"{student.first_name} {student.last_name}",
            'score': score.score
        })

    return jsonify(score_data)

@bp.route('/stop_exam/<int:exam_id>', methods=['POST'])
@login_required
def stop_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    exam.active = 'stopped'
    db.session.commit()
    socketio.emit('exam_stopped', room=exam.code)
    return redirect(url_for('main.exam_results', exam_id=exam_id))

@bp.route('/live_scoreboard/<int:exam_id>')
@login_required
def live_scoreboard(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    students = User.query.filter(User.id.in_(exam_participants.get(exam_id, []))).all()
    return render_template('live_scoreboard.html', exam=exam, students=students)

@bp.route('/exam_results/<int:exam_id>', methods=['GET'])
@login_required
def exam_results(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    final_scores = (db.session.query(Score, User)
                    .join(User, Score.student_id == User.id)
                    .filter(Score.exam_id == exam_id)
                    .order_by(Score.score.desc())
                    .all())
    
    return render_template('exam_results.html', exam=exam, final_scores=final_scores)

@bp.route('/reset_exam/<int:exam_id>', methods=['POST'])
@login_required
def reset_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    Score.query.filter_by(exam_id=exam_id).delete()
    exam.active = 'not_started'
    
    if exam_id in exam_participants:
        del exam_participants[exam_id]
    
    db.session.commit()
    socketio.emit('exam_reset', room=exam.code)
    
    flash(f'Exam "{exam.name}" has been reset and participants have been removed.', 'success')
    return redirect(url_for('main.professor_dashboard'))

@socketio.on('join')
def handle_join(data):
    room = data['room']
    print(f"Room: {room}, Type: {type(room)}")  
    join_room(room)
    emit('join_announcement', {'msg': f"{data['user']} has joined the room."}, room=room)
