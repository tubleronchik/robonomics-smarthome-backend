FROM python:3.6
WORKDIR /app
COPY requirements.txt requirements.txt 
RUN /bin/bash -c 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y'
RUN /bin/bash -c 'source $HOME/.cargo/env; rustup default nightly; python3 -m pip install -r requirements.txt'
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]