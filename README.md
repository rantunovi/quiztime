# Quiztime  
*A web platform for creating, managing, and participating in exams, with instant answer evaluation and live leaderboard updates.*

## Key features
- **For professors**: Create exams, add and modify questions and related data, and monitor student progress in real time
- **For students**: Join exams using a unique code, answer questions, and receive immediate feedback
- **Automated evaluation & leaderboard updates**: Track student scores and progress in real-time, ensuring transparency and competitive aspect
- **Bilingual support**: Switch effortlessly between English and Croatian UI

## How it works?
1. Professor can **create exams**, add multiple-choice questions, define correct answer and number of points it awards. They can also modify or delete exams.
2. Professor opens access to **exam lobby** which displays automatically generated unique exam code
3. Students **join the exam lobby** by entering the exam code, which adds them to list of joined participants
4. When everyone joined, professor can **start the exam**, which redirects students to exam questions, while professor is redirected to live leaderboard
5. Students answer questions one at a time, with **leaderboard** updating with each correct answer
6. When the time is up, professor can **stop the exam** which prevents students from accessing it and takes them back to the homepage
7. After the exam is stopped, **final results** are displayed

## Workflow demo
https://github.com/user-attachments/assets/8fe6b592-0275-40b4-9089-4549fbf678b5

## Tech stack
- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, Javascript
- **Database**: SQLite
- **Real-time communication**: Socket.IO

## Installation
1. Clone the repository
```
git clone https://github.com/a-renato/quiztime.git
cd quiztime
```
2. Install dependencies
```
pip install -r requirements.txt  
```

4. Initialize the database
```
flask db upgrade
```

5. Run the app
```
flask run
```

6. Open your browser and visit:
```
localhost:5000
```

## Using the app with multiple users
To use the app with multiple users simultaneously, each user needs to be logged in in a different web browser. For example:
- User 1: Google Chrome
- User 2: Google Chrome (Incognito Window)
- User 3: Microsoft Edge
etc.
