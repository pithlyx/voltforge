## Server

make sure your network is marked as private in network settings to allow other computers to connect on local netowrk

```bash
netsh interface portproxy add v4tov4 listenaddress=<Windows_IP> listenport=<Windows_Port> connectaddress=<WSL2_VM_IP> connectport=<Flask_API_Port>
```
