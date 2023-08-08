# grpc demo

## 安装

`pip3 install grpcio grpcio_tools`

`python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./cyberdog_app.proto`
## 运行
请先获取到机器人在局域网中的IP，参数分别为：机器人的ip、CA证书、client秘钥、client证书  
`python3 grpc_teleop.py 192.168.xxx.xxx cert/ca-cert.pem cert/client-key.pem cert/client-cert.pem`  
操作方法类似turtlebot3的遥控程序，w、x、a、d分别为前后左右加速，不按键盘时速度保持不变，s为停止，esc为退出  