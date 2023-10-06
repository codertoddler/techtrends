FROM python:3.8
EXPOSE 3111
RUN mkdir /app
COPY ./techtrends/. /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py
CMD [ "python", "app.py" ]