# grpc demo

## 安装

`pip3 install grpcio grpcio_tools`

`python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./cyberdog_app.proto`