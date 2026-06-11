# Exelidoc Website

Official website for Exelidoc — an AI-powered Microsoft Office assistant that helps users work faster in Excel, Word, and PowerPoint.

---

## Features

- Modern landing page
- Download page for Exelidoc installer
- Tutorials page
- Documentation page
- Pricing page
- Responsive design
- Flask backend
- Easy deployment

---

## Project Structure

```text
Exelidoc_Pro_Website/
│
├── app.py
│
├── templates/
│   ├── index.html
│   ├── features.html
│   ├── download.html
│   ├── tutorials.html
│   ├── docs.html
│   └── pricing.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

## Requirements

- Python 3.10+
- Flask

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Exelidoc-Website.git
cd Exelidoc-Website
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Flask:

```bash
pip install flask
```

---

## Running the Website

Start the Flask server:

```bash
python app.py
```

You should see:

```text
* Running on http://127.0.0.1:5000
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

---

## Pages

### Home

Landing page introducing Exelidoc.

### Features

Highlights the major capabilities:

- Excel AI
- Word AI
- PowerPoint AI
- Formula Generation
- Data Analysis

### Download

Allows users to download the latest Exelidoc installer.

Replace:

```html
<a class="btn" href="#">
```

with:

```html
<a class="btn" href="/downloads/Exelidoc_Setup.exe">
```

or your hosted download URL.

### Tutorials

Embed tutorial videos and setup guides.

### Documentation

Technical documentation and usage instructions.

### Pricing

Pricing plans and licensing information.

---

## Deployment

### Render

1. Create a Render account
2. Connect GitHub repository
3. Create a new Web Service
4. Set build command:

```bash
pip install -r requirements.txt
```

5. Set start command:

```bash
gunicorn app:app
```

---

### Railway

1. Create Railway project
2. Connect GitHub
3. Deploy

Railway automatically detects Flask applications.

---

### VPS

Install dependencies:

```bash
pip install flask gunicorn
```

Run:

```bash
gunicorn app:app
```

Use Nginx as a reverse proxy.

---

## Future Improvements

- User accounts
- Analytics dashboard
- Download tracking
- Release notes page
- AI demo videos
- Contact form
- Blog system
- Documentation search
- NVIDIA NIM integration page

---

## About Exelidoc

Exelidoc is designed to bring powerful AI capabilities directly into Microsoft Office workflows.

Users can:

- Generate Excel formulas
- Analyze spreadsheets
- Create Word documents
- Build PowerPoint presentations
- Automate repetitive office tasks

without leaving their workflow.

---

## License

Copyright © Exelidoc

All Rights Reserved.
