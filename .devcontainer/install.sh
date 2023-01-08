sudo apt update -y;
sudo apt install python3 -y;
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1; // make python3 default
sudo apt install libcairo2-dev -y; // cairo dependancy
sudo apt install python3-pip -y;
pip3 install pycairo;