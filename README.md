# The Watchtower
This Project is about an Uptime Monitoring system with Alerting and Status Page. 
This can be used for Web & Infrastructure uptime monitoring. It is built using Streamlit as frontend and FastAPI+Postgres as backend. **All Open Source.**

Project is live for Public use at [The Watchtower](https://watchtower.finanssure.com)

# Why The Watchtower?
1. **Simple** - Clutter-free design. Minimal input required.
2. **Effective** - Developer friendly
3. **Open Source** - You can contribute and make it better
4. **Versatile** - You can use it for i.e. APIs, websites, servers and databases.
5. **Manageable** - You can manage configs through UI, API and Config as Code.
6. **Cloud Agnostic** - Run it on your own server or any cloud
7. **Extensible** - You can add plugins & connector for different services
8. **Enterprise Ready (Upcoming)** 
   1. You can use it for your business with multi-tenancy support
   2. Support Configuration as Code
   3. Private Status Page
   4. Proxy & IP Whitelisting

# Supported Connectors
| Type           | Target                     | Protocols            |
|----------------|----------------------------|----------------------|
| APIs           | REST, GraphQL, SOAP        |                      |
| Websockets     | _(Upcoming)_               |                      |
| Websites       | Public / Private           | HTTP, HTTPS          |
|                | Domain Expiry _(Upcoming)_ |                      |
| Database       | Postgres, MongoDB, Redis   | _(Extensible)_       |
| Servers        | Remote Servers             | SSH, RDP             |
|                | Email _(Upcoming)_         | SMTP, POP3, IMAP     |
|                | DNS _(Upcoming)_           | DNS, DNSSEC          |
|                | File Servers _(Upcoming)_  | FTP, SFTP            |
| Certificates   | _(Upcoming)_               | SSL, TLS             |
| Message Queues | _(Upcoming)_               | RabbitMQ, Kafka, SQS |


# Basic Features
1. [ ] Create monitor
2. [ ] View & Manage monitors
3. [ ] View status page 
4. [ ] View history & connection statistics
5. [ ] Public / Private status page
6. [ ] Create Alert Rules
7. [ ] Send alerts in different channel
8. [ ] Organisation & User management
9. [ ] Manage configs through API
10. [ ] Manage configs through CLI / CI Pipeline

# Areas where contribution is appreciated
1. Scaling the system with container orchestration for public use
2. Adding more connectors for different services
3. Adding more alerting channels
4. Some money or infra support for hosting the system in cloud across the globe

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
streamlit run src/Dashboard.py --server.runOnSave true
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
