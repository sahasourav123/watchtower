# the-watchtower
Simple and effective Uptime Monitoring, Alerting and Status Page for
- Rest APIs
- Websites
- Database
- Servers

# Development Setup
1. Clone the repository
```bash
git clone https://github.com/sahasourav123/the-watchtower.git
```
2. Setup a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```
3. Install the dependencies
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```
4. Run backend application (fastapi app)
```bash
cd backend
export PYTHONPATH=$(pwd)/src
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```
5. Run frontend application (streamlit app)
```bash
cd frontend
export PYTHONPATH=$(pwd)/src
streamlit run src/Home.py --server.runOnSave true
```
6. Build the docker image
```bash
docker compose build
```

# Run the system in docker
- Run the docker container
```bash
docker compose up -d
```
- Clean up (without data)
```bash
docker compose down
```
- Clean up (with data)
```bash
docker compose down -v
```

# Features
- Add a new monitor
- View all monitors
- View monitor details
- Edit a monitor
- Delete a monitor
- View status page
- View history & statistics
