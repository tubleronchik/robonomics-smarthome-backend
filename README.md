## Dependencies 

```
git clone --recursive https://github.com/tubleronchik/robonomics_smarthome_backend
cd robonomics_smarthome_backend
pip3 install -r requirements.txt
```
# Run

```
uvicorn app:app
```
---

# Docker
```
docker compose build
docker compose up 
```
App can be found at  `http://127.0.0.1:8080`