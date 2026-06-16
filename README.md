# CivicFix

CivicFix is an AI-powered civic issue reporting platform that helps citizens report public infrastructure problems through image uploads.

Users can submit issues such as potholes and garbage dumps by uploading a photo and providing a location. The system uses a YOLOv8-based computer vision model to classify the issue and automatically assign it to the appropriate department.

Department officials can view issues assigned to their department, update the issue status, and track progress until resolution. Citizens can monitor the status of their submitted reports through their dashboard.

## Features

* User Registration and Login
* Department Login
* Image Upload for Issue Reporting
* AI-Based Issue Classification using YOLOv8
* Automatic Department Assignment
* Issue Tracking Dashboard
* Status Updates (Pending, Assigned, In Progress, Resolved)
* Role-Based Access Control

## Departments

* Roads Department
* Waste Management Department

## Tech Stack

* Python
* Flask
* MySQL
* YOLOv8
* HTML
* CSS
* Bootstrap 5

## Setup

1. **Clone repository**

   ```bash
   git clone <repository-url>
   cd civicfix
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   ```

   Activate it:

   * Windows: `venv\Scripts\activate`
   * macOS/Linux: `source venv/bin/activate`

3. **Install requirements**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**

   ```env
   SECRET_KEY=your-secret-key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_NAME=civicfix
   ```

5. **Run database setup**

   ```bash
   python setup_db.py
   ```

6. **Run the application**

   ```bash
   python app.py
   ```

   Open: http://127.0.0.1:5000

## Demo Accounts

### Roads Department

* Email: `road@civicfix.com`
* Password: `road123`

### Waste Management Department

* Email: `waste@civicfix.com`
* Password: `waste123`

Citizens can register their own accounts and submit issues.

## Database Reference

See `schema.sql` for the complete database schema.
