FROM python:3.7
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install streamlit
RUN pip install -r requirements.txt
RUN pip install --upgrade streamlit
EXPOSE 8501
COPY . /app
ENTRYPOINT ["streamlit", "run", "/app/main.py"]
