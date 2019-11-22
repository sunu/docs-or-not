FROM python:3.6-slim-stretch

RUN apt-get update
RUN apt-get install -y python3-dev gcc

# Install pytorch and fastai
RUN pip3 install torch==1.3.0+cpu torchvision==0.4.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install fastai

# Install starlette and uvicorn
# RUN pip install starlette uvicorn python-multipart aiohttp

ADD export.pkl export.pkl
ADD export-v2.pkl export-v2.pkl
# ADD app.py /app/app.py
ADD cli.py /app/cli.py

# Run it once to trigger resnet download
RUN python /app/cli.py

# EXPOSE 8008

# Start the server
# CMD ["python", "/app/app.py", "serve"]
ENTRYPOINT ["python", "/app/cli.py"]
