FROM python:3.8
WORKDIR /code
RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
ENV PYTHONPATH "${PYTHONPATH}:/code/"
WORKDIR /code/app
CMD [ "python", "flask-app.py" ]