# SereneAPI

SereneAPI is a backend API built with Flask to support the Serene application. It handles client requests, processes data, and interacts with the database.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/pavellsan8/serene_app_api
   cd serene_app_api
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate  # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To run the API, activate the virtual environment and start the Flask server:
```bash
python app.py
```
The API will be available at `http://127.0.0.1:5000/`.

## Technologies Used
- Python 3.11.0
- Flask
- Flask SQLAlchemy
- Marshmallow
- MySQL / PostgreSQL
