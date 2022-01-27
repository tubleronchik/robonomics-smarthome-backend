## Dependencies 

```

pip3 install -r requirements.txt
```
# Run

```
cd app/
uvicorn app:app
```
---

# Docker
```
docker build --tag app .  
docker run -p 8000:8000 --name smarthome_backend -v scripts:/app/config/ app    
```