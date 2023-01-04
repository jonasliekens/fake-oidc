FROM python:3.10-alpine
MAINTAINER Jonas Liekens <jonas.liekens@brickbit.be>
# Workdir
WORKDIR /app
# Copy app
COPY . /app
# Install dependencies
RUN pip install -r requirements.txt
# Prepare & Run
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]
