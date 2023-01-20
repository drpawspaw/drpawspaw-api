FROM python:3.8.16

# copy project files to docker image
COPY . /

# install build tools
RUN apt update && apt install build-essential

# install requirements
RUN pip install wheel setuptools pip --upgrade
RUN pip install -r requirements.txt

# setup.py file resposible to download the required packages for NLTK
RUN python setup.py

# run the application
CMD ["python", "view.py"]

# expose the endpoint access outside
EXPOSE 7860