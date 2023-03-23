FROM python:3.8.16

# copy project files to docker image
COPY . /

# install build tools
RUN apt update && apt install build-essential

# install requirements
RUN pip install wheel setuptools pip --upgrade
RUN export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
RUN pip install -r requirements.txt
RUN pip install google-cloud-dialogflow 

# setup.py file resposible to download the required packages for NLTK
RUN python setup.py
RUN chmod +x ./run.sh 

# run the application
CMD ./run.sh

# expose the endpoint access outside
EXPOSE 8000
