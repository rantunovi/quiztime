document.addEventListener('DOMContentLoaded', (event) => {
    var socket = io.connect('http://' + window.location.host);
    var studentScores = {};
    var currentQuestionIndex = 0;

    socket.on('connect', () => {
        if (typeof exam_code === 'string' && exam_code.trim() !== '') {
            socket.emit('join', { room: exam_code, user: user_role });
        } else {
            console.error('Exam code is invalid:', exam_code);
        }

        // Handle when student leaves the page (disconnects)
        window.addEventListener('beforeunload', () => {
            socket.emit('student_left_page', { room: exam_code, student_id: current_user_id });
        });
    });

    socket.on('student_joined', function (data) {
        var studentsList = document.getElementById('students_list');
        if (studentsList) {
            var newStudent = document.createElement('li');
            newStudent.innerText = `${data.first_name} ${data.last_name}`;
            studentsList.appendChild(newStudent);

            // Update the student count
            var studentCountElement = document.querySelector('h2 span');
            if (studentCountElement) {
                studentCountElement.innerText = studentsList.children.length;
            }
        }
    });

    socket.on('exam_started', function (data) {
        if (user_role === 'student') {
            window.location.href = data.redirect_url;
        } else if (user_role === 'professor') {
            window.location.href = `/live_scoreboard/${data.exam_id}`; // Redirect professor to live scoreboard
        }
    });

    // Exam Lobby button action on dashboard page
    document.querySelectorAll('#exam-lobby-button').forEach(button => {
        button.addEventListener('click', function () {
            var examId = this.dataset.examId;
            window.location.href = `/exam_lobby/${examId}`;
        });
    });

    if (user_role === 'professor') {
        var startExamButton = document.getElementById('start-exam-button');
        if (startExamButton) {
            startExamButton.addEventListener('click', function () {
                var examId = this.dataset.examId;
                fetch(`/start_exam/${examId}`, {
                    method: 'POST'
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Server responded with status ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            window.location.href = `/live_scoreboard/${examId}`;
                        } else {
                            alert('Failed to start the exam. Please try again.');
                        }
                    })
                    .catch(error => {
                        alert('An error occurred while starting the exam.');
                    });
            });
        }
    }

    function loadQuestion(index) {
        var question = questions[index];
        document.getElementById('question_text').innerText = question.question_text;
        var optionsContainer = document.getElementById('options_container');
        optionsContainer.innerHTML = '';

        var options = ['a', 'b', 'c', 'd'];
        options.forEach(function (option) {
            var optionElement = document.createElement('div');
            optionElement.className = 'option-box';
            optionElement.innerText = question['option_' + option];
            optionElement.onclick = function () {
                submitAnswer(question.id, option);
            };
            optionsContainer.appendChild(optionElement);
        });
    }

    function submitAnswer(questionId, selectedOption) {
        fetch('/submit_answer/' + questionId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answer: selectedOption }),
        }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentQuestionIndex++;
                    if (currentQuestionIndex < questions.length) {
                        loadQuestion(currentQuestionIndex);
                    } else {
                        document.getElementById("question_container").style.display = 'none';
                        setTimeout(function () {
                            alert('You have answered all the questions! Please wait for the final results.');
                            window.location.href = '/join_exam';
                        }, 100);
                    }
                }
            }).catch(error => {
                alert('An error occurred while submitting the answer.');
            });
    }

    socket.on('score_update', function (data) {
        if (user_role === 'professor') {
            fetch(`/get_scores/${data.exam_code}`)
                .then(response => response.json())
                .then(scores => {
                    updateScoreboard(scores);
                })
                .catch(error => {
                    console.error('Failed to fetch scores:', error);
                });
        }
    });

    function updateScoreboard(scores) {
        var scoreboardList = document.getElementById('scoreboard_list');
        if (scoreboardList) {
            var scoreMap = {};
            scores.forEach(score => {
                scoreMap[score.student_id] = score.score;
            });

            var studentItems = scoreboardList.children;
            Array.from(studentItems).forEach(item => {
                var studentId = item.id.replace('student_', '');
                var score = scoreMap[studentId] !== undefined ? scoreMap[studentId] : 0;
                var scoreElement = item.querySelector('span:last-child');
                scoreElement.textContent = score;
            });

            var sortedItems = Array.from(studentItems).sort((a, b) => {
                var scoreA = parseInt(a.querySelector('span:last-child').textContent);
                var scoreB = parseInt(b.querySelector('span:last-child').textContent);
                return scoreB - scoreA;
            });

            scoreboardList.innerHTML = '';
            sortedItems.forEach(item => {
                scoreboardList.appendChild(item);
            });
        }
    }

    socket.on('exam_stopped', function () {
        document.getElementById("question_container").style.display = 'none';
        setTimeout(function () {
            alert('The professor has stopped the exam. Please wait for the final results.');
            window.location.href = '/join_exam';
        }, 100);
    });

    socket.on('exam_reset', function (data) {
        var studentsList = document.getElementById('students_list');
        if (studentsList) {
            studentsList.innerHTML = '';
        }
        document.getElementById("question_container").style.display = 'none';
        setTimeout(function () {
            alert('The professor has reset the exam. Please rejoin the exam using the same code.');
            window.location.href = '/join_exam';
        }, 100);
    });

    loadQuestion(currentQuestionIndex);
    window.submitAnswer = submitAnswer;
});
