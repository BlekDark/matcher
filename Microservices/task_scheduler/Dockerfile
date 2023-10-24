FROM python:3.10

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy --skip-lock

COPY .  .

CMD ["python3", "send_task.py"]