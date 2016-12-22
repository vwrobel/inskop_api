FROM continuumio/miniconda3

# Dinamically replace httpredir.debian.org with a single working domain
# in attempt to "prevent" the "Error reading from server" error.
RUN sed -i "s/httpredir.debian.org/`curl -s -D - http://httpredir.debian.org/demo/debian/ | awk '/^Link:/ { print $2 }' | sed -e 's@<http://\(.*\)/debian/>;@\1@g'`/" /etc/apt/sources.list

# Add backports to apt/sources.list to install ffmpeg on debian

RUN apt-get clean && apt-get update && apt-get -y install apt-utils
RUN apt-get -y install vim --fix-missing
RUN apt-get -y install build-essential
RUN apt-get -y install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libpq-dev gcc --fix-missing
RUN apt-get -y install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev --fix-missing
RUN apt-get -y install python-psycopg2 --fix-missing
RUN pip install psycopg2~=2.6
RUN conda install conda-build
RUN conda install cmake
RUN conda list
RUN git clone https://github.com/vwrobel/conda-opencv3
RUN cd conda-opencv3 && conda config --add channels menpo && conda build conda/
RUN conda install /opt/conda/conda-bld/linux-64/opencv3-3.1.0-py35_0.tar.bz2
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD requirements.txt /usr/src/app
RUN pip install -r requirements.txt
ADD . /usr/src/app
EXPOSE 8000
# To prevent error from lib1394 (cam driver)
RUN echo 'ln /dev/null /dev/raw1394' >> ~/.bashrc