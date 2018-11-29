FROM python:3.6.6

COPY requirements_dev.txt /requirements_dev.txt

RUN pip3 install --upgrade pip \
&& pip3 install -r requirements_dev.txt \
&& rm -r /root/.cache/pip

RUN mkdir code && mkdir ~/.scopus 

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ./entrypoint.sh

#https://stackoverflow.com/a/36388856
RUN echo 'alias jn="jupyter-notebook --ip="0.0.0.0" --no-browser --port=8000 --allow-root"' >> ~/.bashrc

RUN python3 -m pip install git+https://github.com/spatialaudio/nbsphinx.git@master

RUN apt-get update && apt-get install pandoc -y

WORKDIR /code
