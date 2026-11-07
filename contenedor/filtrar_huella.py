#!/usr/bin/env python3
"""Discard laser returns inside Dingo-O's published Nav2 footprint only."""
import math
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener, TransformException
class FootprintFilter(Node):
    def __init__(self):
        super().__init__('ws3_lidar_footprint_filter', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.buffer=Buffer(); self.listener=TransformListener(self.buffer,self)
        self.pub=self.create_publisher(LaserScan,'/do100_0000/sensors/lidar2d_0/scan_filtrado',qos_profile_sensor_data)
        self.create_subscription(LaserScan,'/do100_0000/sensors/lidar2d_0/scan',self.scan,qos_profile_sensor_data)
        self.logged=False
    def scan(self,msg):
        try: tr=self.buffer.lookup_transform('base_link',msg.header.frame_id,Time()).transform
        except TransformException: return
        q=tr.rotation
        # Full quaternion rotation, including any fixed sensor tilt.
        R=((1-2*(q.y*q.y+q.z*q.z),2*(q.x*q.y-q.z*q.w)),
           (2*(q.x*q.y+q.z*q.w),1-2*(q.x*q.x+q.z*q.z)))
        ranges=list(msg.ranges); removed=0
        for i,r in enumerate(ranges):
            if not math.isfinite(r): continue
            a=msg.angle_min+i*msg.angle_increment; x=r*math.cos(a); y=r*math.sin(a)
            bx=R[0][0]*x+R[0][1]*y+tr.translation.x
            by=R[1][0]*x+R[1][1]*y+tr.translation.y
            if abs(bx)<=0.343 and abs(by)<=0.2585:
                ranges[i]=float('nan'); removed+=1
        msg.ranges=ranges; self.pub.publish(msg)
        if not self.logged:
            self.get_logger().info(f'Footprint filter: {removed}/{len(ranges)} interior returns discarded; exterior readings unchanged')
            self.logged=True
rclpy.init(); n=FootprintFilter()
try: rclpy.spin(n)
except KeyboardInterrupt: pass
finally:
    n.destroy_node()
    if rclpy.ok(): rclpy.shutdown()
