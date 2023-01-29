FROM python:3.9-slim

# Set the working directory
WORKDIR /streamlit_app

# Create a volume at /streamlit_app/
VOLUME /streamlit_app/

# Copy the current directory contents into the container at /app
COPY . /streamlit_app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Install spaCy model for French
RUN python -m spacy download fr_core_news_sm

# Exposing port 5000 
EXPOSE 8501

# Run the app server
ENTRYPOINT ["streamlit", "run", "Hello.py", "--server.port=8501", "--server.address=0.0.0.0"]