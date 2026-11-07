#!/usr/bin/env python3
"""Explore the live SLAM map through Nav2; never creates a map from world geometry.

Run inside the Jazzy container after mapping.launch.py and Clearpath nav2.launch.py.
The final map must still be inspected and saved with map_saver_cli.
"""
import argparse
import json
import math
import time

import numpy as np
from scipy import ndimage
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from rclpy.time import Time
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.action import NavigateToPose
from tf2_ros import Buffer, TransformListener, TransformException


class Explorer(Node):
    def __init__(self, max_goals, max_sim_seconds, bounds=None):
        super().__init__('ws3_frontier_explorer',
                         parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.map = None
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                         reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(OccupancyGrid, '/do100_0000/map', self.receive_map, qos)
        self.client = ActionClient(self, NavigateToPose, '/do100_0000/navigate_to_pose')
        self.max_goals, self.max_seconds = max_goals, max_sim_seconds
        self.bounds = bounds
        self.visited = []
        self.home = None
        self.active = False
        self.goal_handle = None
        self.goal = None
        self.request_home = False
        self.home_goal = False
        self.cancel_sent = False
        self.finished = False
        self.exit_code = 0
        self.start_time = None
        self.next_plan = 0.0
        self.empty_count = 0
        self.create_timer(1.0, self.tick)

    def now(self):
        return self.get_clock().now().nanoseconds / 1e9

    def event(self, name, **data):
        print(json.dumps({'event': name, 'sim_time': self.now(),
                          'wall_time_unix': time.time(), **data}), flush=True)

    def receive_map(self, msg):
        self.map = msg

    def pose(self):
        try:
            tr = self.buffer.lookup_transform(self.map.header.frame_id, 'base_link', Time())
            return tr.transform.translation.x, tr.transform.translation.y
        except TransformException:
            return None

    def choose_frontier(self, pose):
        msg = self.map
        grid = np.array(msg.data, dtype=np.int16).reshape(msg.info.height, msg.info.width)
        res = msg.info.resolution
        origin = msg.info.origin
        q = origin.orientation
        yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
        c, s = math.cos(yaw), math.sin(yaw)
        dx, dy = pose[0]-origin.position.x, pose[1]-origin.position.y
        col = int((c*dx+s*dy)/res)
        row = int((-s*dx+c*dy)/res)
        if not (0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]):
            return None
        unknown = grid < 0
        clearance = ndimage.distance_transform_edt(grid < 50)*res
        traversable = (grid >= 0) & (grid < 20) & (clearance > 0.30)
        labels, _ = ndimage.label(traversable, np.ones((3, 3)))
        label = labels[row, col]
        if label == 0:
            rr, cc = np.where(traversable)
            if not len(rr):
                return None
            d2 = (rr-row)**2 + (cc-col)**2
            nearest = int(np.argmin(d2))
            if d2[nearest]*res*res > 0.75**2:
                return None
            label = labels[rr[nearest], cc[nearest]]
        distance_unknown = ndimage.distance_transform_edt(~unknown)*res
        frontier = ((labels == label) & (clearance > 0.34) &
                    (distance_unknown >= 0.05) & (distance_unknown <= 0.60))
        clusters, count = ndimage.label(frontier, np.ones((3, 3)))
        radius = max(1, round(2.0/res))
        information = ndimage.uniform_filter(unknown.astype(np.float32), size=2*radius+1)
        best = None
        best_score = -1.0
        for n, region in enumerate(ndimage.find_objects(clusters), 1):
            if region is None:
                continue
            rr, cc = np.where(clusters[region] == n)
            if len(rr) < 5:
                continue
            rr, cc = rr+region[0].start, cc+region[1].start
            gx, gy = (cc+0.5)*res, (rr+0.5)*res
            xx = origin.position.x+c*gx-s*gy
            yy = origin.position.y+s*gx+c*gy
            valid = np.hypot(xx-pose[0], yy-pose[1]) > 0.65
            if self.bounds is not None:
                xmin, ymin, xmax, ymax = self.bounds
                valid &= ((xx >= self.home[0]+xmin) & (xx <= self.home[0]+xmax) &
                          (yy >= self.home[1]+ymin) & (yy <= self.home[1]+ymax))
            for x, y in self.visited:
                valid &= np.hypot(xx-x, yy-y) > 0.85
            if not valid.any():
                continue
            rr, cc, xx, yy = rr[valid], cc[valid], xx[valid], yy[valid]
            # Prefer reachable frontiers with useful unknown area and short travel.
            distances = np.hypot(xx-pose[0], yy-pose[1])
            scores = information[rr, cc] / (1.0+0.35*distances)
            k = int(np.argmax(scores))
            if scores[k] > best_score:
                best_score = float(scores[k])
                best = (float(xx[k]), float(yy[k]))
        self.event('map_evaluated', width=msg.info.width, height=msg.info.height,
                   resolution=res, known_free_cells=int(np.sum((grid >= 0) & (grid < 20))),
                   occupied_cells=int(np.sum(grid >= 50)), frontier_clusters=count,
                   chosen_goal=best)
        return best

    def send(self, xy, pose, home=False):
        self.goal, self.home_goal = xy, home
        self.active, self.cancel_sent = True, False
        self.sent_at = self.now()
        goal = NavigateToPose.Goal()
        goal.behavior_tree = '/ws/contenedor/exploracion_bt.xml'
        goal.pose.header.frame_id = self.map.header.frame_id
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x, goal.pose.pose.position.y = xy
        angle = math.atan2(xy[1]-pose[1], xy[0]-pose[0])
        goal.pose.pose.orientation.z = math.sin(angle/2)
        goal.pose.pose.orientation.w = math.cos(angle/2)
        self.event('goal_sent', x=xy[0], y=xy[1], returning_home=home)
        self.client.send_goal_async(goal).add_done_callback(self.accepted)

    def accepted(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.completed(None)
            return
        self.goal_handle.get_result_async().add_done_callback(self.completed)

    def completed(self, future):
        status = future.result().status if future else -1
        self.event('goal_result', status=status, x=self.goal[0], y=self.goal[1],
                   returning_home=self.home_goal)
        self.active, self.goal_handle = False, None
        if self.home_goal:
            self.exit_code = 0 if status == 4 else 2
            self.event('exploration_stopped', reason='home_reached' if status == 4 else 'home_not_reached',
                       explored_goals=len(self.visited))
            self.finished = True
        else:
            self.visited.append(self.goal)
            self.next_plan = self.now()+3.0

    def tick(self):
        if self.finished or self.map is None:
            return
        pose = self.pose()
        if pose is None or not self.client.server_is_ready():
            return
        now = self.now()
        if self.home is None:
            self.home, self.start_time = pose, now
            self.event('exploration_started', home=list(pose))
        if now-self.start_time > self.max_seconds or len(self.visited) >= self.max_goals:
            self.request_home = True
        if self.active:
            timeout = now-self.sent_at > (180 if self.home_goal else 120)
            if self.goal_handle and not self.cancel_sent and (timeout or (self.request_home and not self.home_goal)):
                self.cancel_sent = True
                self.event('goal_cancel_requested', timeout=timeout)
                self.goal_handle.cancel_goal_async()
            return
        if now < self.next_plan:
            return
        if self.request_home:
            self.send(self.home, pose, home=True)
            return
        goal = self.choose_frontier(pose)
        if goal is None:
            self.empty_count += 1
            self.next_plan = now+3.0
            if self.empty_count >= 3:
                self.request_home = True
                self.event('no_more_frontiers', note='Requires visual inspection; not a guarantee of full coverage.')
            return
        self.empty_count = 0
        self.send(goal, pose)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume-log', help='Continue the same SLAM session from an earlier JSONL log')
    parser.add_argument('--max-goals', type=int, default=35)
    parser.add_argument('--max-sim-seconds', type=float, default=600)
    parser.add_argument('--bounds', type=float, nargs=4, metavar=('XMIN','YMIN','XMAX','YMAX'),
                        help='Exploration limits relative to the initial map pose; does not generate occupancy data.')
    args, ros_args = parser.parse_known_args()
    rclpy.init(args=ros_args)
    node = Explorer(args.max_goals, args.max_sim_seconds, args.bounds)
    if args.resume_log:
        with open(args.resume_log) as f:
            for line in f:
                try: e = json.loads(line)
                except ValueError: continue
                if e.get('event') == 'exploration_started':
                    node.home = tuple(e['home']); node.start_time = e['sim_time']
                if e.get('event') == 'goal_result' and not e.get('returning_home'):
                    node.visited.append((e['x'], e['y']))
        node.event('exploration_resumed', previous_goals=len(node.visited))
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.2)
    except KeyboardInterrupt:
        if node.goal_handle is not None:
            future = node.goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, future, timeout_sec=5)
        node.exit_code = 130
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    raise SystemExit(node.exit_code)


if __name__ == '__main__':
    main()
