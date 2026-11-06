"""Pruebas numéricas independientes de ROS y Gazebo: python3 -m unittest discover -s tests -v."""
import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'omni_workshop'))
from omni_workshop.kinematics import forward_kinematics, inverse_kinematics, world_to_robot
from omni_workshop.trajectory import FIGURES


class ModelTests(unittest.TestCase):
    def test_basic_wheel_directions(self):
        self.assertEqual(inverse_kinematics(0.2, 0, 0), (4, 4, 4, 4))
        self.assertEqual(inverse_kinematics(0, 0.2, 0), (-4, 4, 4, -4))
        fl, fr, rl, rr = inverse_kinematics(0, 0, 1)
        self.assertLess(fl, 0)
        self.assertEqual(fl, rl)
        self.assertEqual(fr, rr)
        self.assertAlmostEqual(fr, 9.408)

    def test_rotated_reference(self):
        vx, vy, w = world_to_robot(math.pi / 2, 0.2, 0, 0.3)
        self.assertAlmostEqual(vx, 0)
        self.assertAlmostEqual(vy, -0.2)
        self.assertEqual(w, 0.3)

    def test_round_trip(self):
        rng = random.Random(3)
        for _ in range(100):
            velocity = [rng.uniform(-1, 1) for _ in range(3)]
            result = forward_kinematics(*inverse_kinematics(*velocity))
            for actual, expected in zip(result, velocity):
                self.assertAlmostEqual(actual, expected)

    def test_trajectory_continuity_and_clearance(self):
        for name in ('JRL', 'prueba_omni'):
            figure = FIGURES[name]()
            previous = (0, 0, 0)
            for duration, state in figure.segments:
                self.assertGreater(duration, 0)
                for a, b in zip(state(0)[:3], previous):
                    self.assertAlmostEqual(a, b)
                previous = state(duration)[:3]
                for i in range(101):
                    x, y, theta, dx, dy, w = state(duration * i / 100)
                    self.assertTrue(all(math.isfinite(v) for v in (x, y, theta, dx, dy, w)))
                    self.assertLessEqual(abs(x), 2.5)
                    self.assertLessEqual(abs(y - 1.5), 2.5)
                    # Finite difference checks derivative of each segment.
                    if 0 < i < 100:
                        t = duration * i / 100
                        before, after = state(t - 1e-6), state(t + 1e-6)
                        for k, derivative in enumerate((dx, dy, w)):
                            self.assertAlmostEqual((after[k] - before[k]) / 2e-6, derivative, places=6)
            self.assertEqual(figure(figure.duration + 1)[3:], (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
