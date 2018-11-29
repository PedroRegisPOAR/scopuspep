

##Running while developping


python3 -m pip install git+https://github.com/pedroregispoar/scopuspep.git@master


Build the image:

docker build -t scopuspep .


To run:

With port:

docker run -it --rm -v "$(pwd)":/code:Z \
-v "$(pwd)"/$DIRECTORY_SCOPUS:/root/$DIRECTORY_SCOPUS:Z \
-e API_KEY=$API_KEY -e DIRECTORY_SCOPUS=$DIRECTORY_SCOPUS \
-p 8000:8000 scopuspep bash

Without port:

docker run -it --rm -v "$(pwd)":/code:Z \
-v "$(pwd)"/$DIRECTORY_SCOPUS:/root/$DIRECTORY_SCOPUS:Z \
-e API_KEY=$API_KEY -e DIRECTORY_SCOPUS=$DIRECTORY_SCOPUS \
 scopuspep bash


To run tests:

python3 -m unittest discover

