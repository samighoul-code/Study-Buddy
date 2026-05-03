# منصة رياضيات المرحلة المتوسطة

A full Arabic RTL educational platform for middle school students (grades 7-9) built with Python/Flask.

## Architecture

- `main.py` — Flask app with all routes and API endpoints
- `logic.py` — Answer checking and score calculation
- `data/questions.json` — Full question bank (6 topics, 48 questions)
- `data/student.json` — Student data persistence (points, badges, tasks, progress)
- `templates/base.html` — Arabic RTL base layout with navigation
- `templates/dashboard.html` — Home dashboard with stats, level, badges
- `templates/math.html` — Topic selection grid with progress bars
- `templates/topic.html` — Interactive question cards with instant feedback
- `templates/tasks.html` — Task management with Kanban-style board

## Features

- 6 math topics for grades 7-9 (quadratic functions, equations, transformations, systems, inequalities, linear equations)
- 48 questions organized by topic and difficulty (easy/medium/hard)
- Points system: easy=10, medium=20, hard=30 points
- 5 student levels based on points
- 8 achievement badges
- Task management with priority, subject, due date, status (todo/in_progress/done)
- Full Arabic RTL UI with Cairo font
- JSON-based data persistence (no database needed)
- Warm purple/green color scheme

## Running

The app runs on port 5000 via `python main.py`. Workflow: "Start application".

## Dependencies

- Flask (Python web framework)

## Design

- Direction: RTL (Arabic)
- Primary color: #7C3AED (purple)
- Font: Cairo (Google Fonts)
- Rounded cards, gamified progress, student-friendly icons
