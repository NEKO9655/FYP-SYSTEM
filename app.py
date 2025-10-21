from flask import Flask, render_template

app = Flask(__name__)

mock_schedule = [
    {
        "time": "10:00 AM - 10:30 AM",
        "student": "Ling Jia Qi",
        "title": "Automated Timetabling Module",
        "supervisor": "Dr. Khairunnisa"
    },
    {
        "time": "10:30 AM - 11:00 AM",
        "student": "Student B",
        "title": "AI-Powered Chatbot for University Services",
        "supervisor": "Dr. Smith"
    },
    {
        "time": "11:00 AM - 11:30 AM",
        "student": "Student C",
        "title": "Data Visualization for Sales Analytics",
        "supervisor": "Dr. Jones"
    }
]

mock_lecturers = [
    {"name": "Dr. Khairunnisa", "status": "Available"},
    {"name": "Dr. Smith", "status": "Unavailable"},
    {"name": "Dr. Jones", "status": "Available"}
]

@app.route('/')
def index():
    return render_template('index.html', schedule=mock_schedule, lecturers=mock_lecturers)

if __name__ == '__main__':
    app.run(debug=True)