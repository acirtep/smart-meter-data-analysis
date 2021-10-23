# demo-postgres-python
Data versioning with postgres and python

This repo is used to detail what data versioning is.

1. Run `docker-compose up --build`
2. Run demo.py inside the python app container:
```
petra1$ docker ps
CONTAINER ID        IMAGE                             COMMAND  ....                
c9a8036c5e80        demo-postgres-python_python_app   "tail -f /dev/null" 
```
- `docker exec -it c9a8036c5e80 /bin/bash`
- `root@c9a8036c5e80:/usr/src/app# python src/demo.py`
3. Or simply use `ipython` for interactive Python
