FROM python:3.6-slim
RUN mkdir /app/sock/ -p
COPY . /app/LoginWeb/
RUN pip3 install -e /app/LoginWeb && \
    pip3 install gunicorn docker

RUN useradd -r user
RUN chown -R user /app
USER user
WORKDIR /app

# activate the flask environment
EXPOSE 5000
CMD ["gunicorn", "tzfserver:app", "-b", "0.0.0.0:5000"]
