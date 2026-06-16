# CivicFix

A civic issue reporting platform where citizens submit problems with photos, AI classifies them, and the relevant department manages resolution.

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

   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install requirements**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**

   Create a `.env` file in the project root:

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

   This creates the database, tables, default departments, and demo accounts. No manual SQL is required.

6. **Run the application**

   ```bash
   python app.py
   ```

   Open http://127.0.0.1:5000 in your browser.

## Demo Accounts

Use these department accounts to explore the department dashboard:

**Roads Department**

- Email: `road@civicfix.com`
- Password: `road123`

**Waste Management Department**

- Email: `waste@civicfix.com`
- Password: `waste123`

Citizens can register a normal user account from the registration page.

## Database Reference

See `schema.sql` for the full database schema.
