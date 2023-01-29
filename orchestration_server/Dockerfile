FROM apache/airflow:latest

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip3 install --user --upgrade pip
RUN pip3 install --no-cache-dir --user -r /requirements.txt

# Install spaCy model for French
RUN python -m spacy download fr_core_news_sm
