import os
import select
import sys
import time

if os.name == 'nt':
    import msvcrt
    print('os.name is nt')
else:
    import termios
    import tty 
    print('os.name is', os.name)

import grpc
import json
import cyberdog_app_pb2
import cyberdog_app_pb2_grpc

class Client:
    def __init__(self, cyberdog_ip: str):
        chennel = grpc.insecure_channel(cyberdog_ip + ':50052')
        self.__stub = cyberdog_app_pb2_grpc.GrpcAppStub(chennel)
        print('Client is ready.')

    def sendMsg(self, name_code, params):
        result_list = self.__stub.sendMsg(
            cyberdog_app_pb2.SendRequest(
                nameCode=name_code,
                params=params), 0.1)
        # print('msg has sent')

class Teleop:
    def __init__(self, acc=[1.0, 0.0, 1.0], freq=10.0, max_vel=[0.5, 0.0, 0.2]):
        self.__vel = [0.0, 0.0, 0.0]
        self.__acc = acc
        self.__freq = freq
        self.__max_vel = max_vel
        self.__settings = None
        if os.name != 'nt':
            self.__settings = termios.tcgetattr(sys.stdin)
        print('Teleop is ready')

    def updateVel(self, delta_vel: list):
        for i in range(0, 3):
            self.__vel[i] += delta_vel[i]
            if self.__vel[i] > self.__max_vel[i]:
                self.__vel[i] = self.__max_vel[i]
        print('vel:', self.__vel)
        return self.__vel

    def __getKey(self, settings):
        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key
         	
    def getVelFromKey(self):
        key = self.__getKey(self.__settings)
        delta_vel = [0.0, 0.0, 0.0]
        if key == '\x1B':
            return (0, [])
        elif key == 'w' or key == 'W':
            delta_vel[0] = self.__acc[0] / self.__freq
        elif key == 'x' or key == 'X':
            delta_vel[0] = -self.__acc[0] / self.__freq
        elif key == 'a' or key == 'A':
            delta_vel[2] = self.__acc[2] / self.__freq
        elif key == 'd' or key == 'd':
            delta_vel[2] = -self.__acc[2] / self.__freq
        elif key == 's' or key == 'S':
            delta_vel[0] = -self.__vel[0]
            delta_vel[2] = -self.__vel[2]
        return (1002, delta_vel)

class ProtoEncoder:
    def encodeVel(self, vel):
        cmd = {}
        cmd['motion_id'] = 303
        cmd['cmd_type'] = 1
        cmd['cmd_source'] = 3
        cmd['value'] = 0
        cmd['step_height'] = [0.06,0.06]
        cmd['vel_des'] = vel
        return json.dumps(cmd)

if __name__ == '__main__':
    if len(sys.argv) == 0:
        print('Please input gRPC server IP')
        exit()
    grpc_client = Client(sys.argv[1])
    teleop = Teleop()
    encoder = ProtoEncoder()
    while True:
        result, delta_vel = teleop.getVelFromKey()
        if result == 0:
            print('exit')
            exit()
        vel = teleop.updateVel(delta_vel)
        json_str = encoder.encodeVel(vel)
        grpc_client.sendMsg(1002, json_str)
        
