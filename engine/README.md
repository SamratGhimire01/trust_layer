# 1. Open the Terminal on the Mac and move into the backend folder
cd path/to/trustlayer/engine

# 2. Check the Python version to make sure it is 3.10+
python3 --version

# 3. Create a clean virtual environment sandbox
python3 -m venv venv

# 4. Activate the virtual environment
source venv/bin/activate

# 5. Install all essential backend packages from the requirements.txt file at once
pip install -r requirements.txt

# 6. Launch the live FastAPI server
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload