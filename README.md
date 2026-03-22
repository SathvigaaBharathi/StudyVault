# StudyVault

A Smart Document Notes Organizer for students to upload, tag, and track study materials.

## Technologies

- Python / Flask
- MySQL (via flask-mysqldb)
- HTML5, Bootstrap 5, jQuery
- Werkzeug (file handling & password hashing)

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/studyvault.git
   cd studyvault
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database
   - Open MySQL and run:
   ```bash
   mysql -u root -p < database.sql
   ```
   - Create a `.env` file in the project root with your credentials:
   ```
   SECRET_KEY=your_secret_key
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=studyvault
   ```

4. Run the app
   ```bash
   python app.py
   ```

5. Open your browser at `http://127.0.0.1:5000`

## Usage

- Register an account and login
- Upload study documents (PDF, DOCX, PPTX)
- Tag documents by subject and difficulty
- View your dashboard for usage stats
- Filter and search documents
- Download or delete documents
- Document status (Active / Fading / Cold) updates automatically based on last opened date

### Deployed link

https://studyvault-sjsy.onrender.com/
