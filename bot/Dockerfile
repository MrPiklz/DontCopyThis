FROM python:3.10-alpine
WORKDIR /BOT
COPY . /BOT
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev python3-dev musl-dev
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python",  "./TG.py"]