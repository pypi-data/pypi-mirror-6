
SOURCES=  osm.py osmlib.py osmlevmar.py  osmmodes.py

all: build install

build: setup.py $(SOURCES) 
	python setup.py build	

install: setup.py $(SOURCES)  
	python setup.py install --home=$(HOME)/

clean:
	rm -fr build
