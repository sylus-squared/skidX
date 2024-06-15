This is not finished <br/>
To setup inetsim on the server run the folowing commands<br/>
sudo su<br/>
echo "deb http://www.inetsim.org/debian/ binary/" > /etc/apt/sources.list.d/inetsim.list<br/>
wget -O - http://www.inetsim.org/inetsim-archive-signing-key.asc | apt-key add -<br/>
apt update<br/>
apt install inetsim<br/>

Edit the config file in /etc/inetsim/inetsim.conf<br/>

Make a directory for results:<br/>
mkdir analysis<br/>

cp /etc/inetsim/inetsim.conf analysis<br/>
sudo cp -r /var/lib/inetsim analysis/data<br/>
sudo chmod -R 777 data<br/>