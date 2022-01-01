## Dependencies 

```
pip3 install fastapi
pip3 install uvicorn
pip3 install jinja2
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
docker run -p 8000:8000 app    
```