#!/bin/bash

sudo apt update
sudo apt -y install make
sudo apt -y install g++
sudo apt -y install libsctp-dev lksctp-tools
sudo apt -y install iproute2
sudo apt -y install snapd
sudo snap install cmake --classic
export PATH=$PATH:/snap/bin
git clone https://github.com/aligungr/UERANSIM.git
cd UERANSIM/
sudo make
#config
cp /local/repository/config/ue.yaml config/
cp /local/repository/config/enb.yaml config/
sudo sed -i 's/imsi-901700000000001/$1/g' config/ue.yaml
sudo sed -i 's/gtpIp: 127.0.0.1/gtpIp: $2/g' config/enb.yaml
sudo sed -i 's/ngapIp: 127.0.0.1/ngapIp: $2/g' config/enb.yaml