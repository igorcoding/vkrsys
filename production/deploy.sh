#! /usr/bin/env bash

sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get install -y git

sudo apt-get install -y mysql-client libmysqlclient-dev

git clone https://github.com/igorcoding/vkrsys.git
cd vkrsys
git submodule update --init
sudo apt-get install -y python2.7-dev python-pip python-virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
cd -


git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg
sudo apt-get install -y libmp3lame0 libmp3lame-dev libx264-dev x264 nasm
sudo apt-get install -y -f
./configure --enable-gpl --enable-version3 --enable-nonfree --enable-postproc --enable-libmp3lame --enable-libx264
make
sudo make install
cd -



cd libs/dejavu/
sudo apt-get install -y libblas-dev liblapack-dev portaudio19-dev
pip install numpy
pip install scipy
pip install --allow-external PyAudio --allow-unverified PyAudio -r requirements.txt
cd -


cd libs/rsys/rsys-python
rm -rf build/
python setup.py install
cd -


sudo apt-get install -y nginx supervisor

sudo mkdir -p /www
sudo cp -a vkrsys /www/

cd /www/vkrsys
cd production
sudo ln -s /www/vkrsys/production/supervisor_conf.d/vkrsys.conf /etc/supervisor/conf.d/

sudo supervisorctl reread
sudo supervisorctl update

sudo ln -s /www/vkrsys/production/nginx.conf/vkrsys /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/vkrsys /etc/nginx/sites-enabled/vkrsys
sudo rm /etc/nginx/sites-enabled/default

sudo nginx -s reload
