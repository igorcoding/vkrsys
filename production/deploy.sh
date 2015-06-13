#! /usr/bin/env bash

sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get install -y git build-essential cmake
yes | sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install -y gcc-4.9 g++-4.9 cpp-4.9 gfortran-4.9
sudo rm /usr/bin/gcc \
		/usr/bin/cpp \
		/usr/bin/g++ \
		/usr/bin/gfortran \
		/usr/bin/x86_64-linux-gnu-gcc \
		/usr/bin/x86_64-linux-gnu-g++ \
		/usr/bin/x86_64-linux-gnu-cpp \
		/usr/bin/x86_64-linux-gnu-gcc-ar \
		/usr/bin/x86_64-linux-gnu-gcc-nm \
		/usr/bin/x86_64-linux-gnu-gcov \
		/usr/bin/x86_64-linux-gnu-gfortran

sudo ln -s /usr/bin/gcc-4.9 /usr/bin/gcc
sudo ln -s /usr/bin/cpp-4.9 /usr/bin/cpp
sudo ln -s /usr/bin/g++-4.9 /usr/bin/g++
sudo ln -s /usr/bin/gfortran-4.9 /usr/bin/gfortran
sudo ln -s /usr/bin/x86_64-linux-gnu-gcc-4.9 /usr/bin/x86_64-linux-gnu-gcc
sudo ln -s /usr/bin/x86_64-linux-gnu-g++-4.9 /usr/bin/x86_64-linux-gnu-g++
sudo ln -s /usr/bin/x86_64-linux-gnu-cpp-4.9 /usr/bin/x86_64-linux-gnu-cpp
sudo ln -s /usr/bin/x86_64-linux-gnu-gcc-ar-4.9 /usr/bin/x86_64-linux-gnu-gcc-ar
sudo ln -s /usr/bin/x86_64-linux-gnu-gcc-nm-4.9 /usr/bin/x86_64-linux-gnu-gcc-nm
sudo ln -s /usr/bin/x86_64-linux-gnu-gcov-4.9 /usr/bin/x86_64-linux-gnu-gcov
sudo ln -s /usr/bin/x86_64-linux-gnu-gfortran-4.9 /usr/bin/x86_64-linux-gnu-gfortran

sudo apt-get install -y mysql-client libmysqlclient-dev

sudo mkdir -p /www
cd /www
sudo git clone https://github.com/igorcoding/vkrsys.git
git submodule update --init
sudo apt-get install -y python2.7-dev python-pip python-virtualenv
sudo virtualenv env
PYTHONBIN=/www/vkrsys/env/bin
$PYTHONBIN/pip install -r vkrsys/requirements.txt

cd /usr/local/src
sudo git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg
sudo apt-get install -y libmp3lame0 libmp3lame-dev libx264-dev x264 nasm
sudo apt-get install -y -f
sudo ./configure --enable-gpl --enable-version3 --enable-nonfree --enable-postproc --enable-libmp3lame --enable-libx264
sudo make
sudo make install


cd /www/vkrsys/libs/dejavu/
sudo apt-get install -y libblas-dev liblapack-dev portaudio19-dev libpng12-dev libfreetype6-dev
$PYTHONBIN/pip install numpy
$PYTHONBIN/pip install scipy
$PYTHONBIN/pip install --allow-external PyAudio --allow-unverified PyAudio -r requirements.txt
$PYTHONBIN/python setup.py install


cd /usr/local/src
sudo apt-get install build-essential python-dev autotools-dev libicu-dev libbz2-dev
sudo wget http://downloads.sourceforge.net/project/boost/boost/1.57.0/boost_1_57_0.tar.gz
sudo tar -xzvf boost_1_57_0.tar.gz
sudo chmod 777 boost_1_57_0
cd boost_1_57_0
n=`cat /proc/cpuinfo | grep "cpu cores" | uniq | awk '{print $NF}'`
sudo ./bootstrap.sh
sudo ./b2 -j $n install
sudo ldconfig
cd -

sudo wget http://downloads.mysql.com/archives/get/file/mysql-connector-c%2B%2B-1.1.4.tar.gz
sudo tar -xzvf mysql-connector-c++-1.1.4.tar.gz
sudo chmod 777 mysql-connector-c++-1.1.4
cd mysql-connector-c++-1.1.4
sudo cmake .
sudo make
sudo make install
sudo ldconfig
cd -

cd -
cd /www/vkrsys/libs/rsys/rsys-python
rm -rf build/
$PYTHONBIN/python setup.py install
cd -


sudo apt-get install -y nginx supervisor

cd /www/vkrsys
cd production
mkdir -p logs
sudo ln -s /www/vkrsys/production/supervisor_conf.d/vkrsys.conf /etc/supervisor/conf.d/

sudo supervisorctl reread
sudo supervisorctl update

sudo ln -s /www/vkrsys/production/nginx.conf/vkrsys /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/vkrsys /etc/nginx/sites-enabled/vkrsys
sudo rm /etc/nginx/sites-enabled/default

sudo nginx -s reload
