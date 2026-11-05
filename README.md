
```bash
# check if Raspberry Pi is reachable
ping raspberrypi.local

# generate SSH key
ssh-keygen

# send public key to Raspberry Pi
cd ~/.ssh/
ssh-copy-id -i id_{tab} pi@raspberrypi.local

# connect to Raspberry Pi
ssh pi@raspberrypi.local


# Wi-Fi configuration
nmcli dev wifi list
sudo nmcli dev wifi connect "SSID_NAME" password "WIFI_PASSWORD"

# update packages
sudo apt update
sudo apt upgrade -y

# install git
sudo apt install git -y

# install tmux
sudo apt install tmux

# install julia 
curl -fsSL https://install.julialang.org | sh

# activate the local inverement
cd code

mode packge with ]

# activate the local env
activate .

# install a new packge
add packge_name

# start a script.jl
include("script.jl")

PS C:\Users\omarm> Test-NetConnection test.mosquitto.org -Port 8883


ComputerName     : test.mosquitto.org
RemoteAddress    : 54.36.178.49
RemotePort       : 8883
InterfaceAlias   : Wi-Fi
SourceAddress    : 192.168.43.89
TcpTestSucceeded : True

