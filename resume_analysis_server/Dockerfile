# 
FROM python:3.9

# Create and set the working directory
WORKDIR /resume_analysis_server

# Copy the requirements file
COPY ./requirements.txt /resume_analysis_server/requirements.txt

# Install the requirements
RUN pip install --no-cache-dir --upgrade -r /resume_analysis_server/requirements.txt

# Copy the source code
COPY ./src /resume_analysis_server/src

# Run the app server
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "4200"]