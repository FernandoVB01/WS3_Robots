"""Cinemática mecanum de 45 grados; SI, orden FL, FR, RL, RR."""
import math

R = 0.05
LX = 0.285
LY = 0.1854


def world_to_robot(theta, dx, dy, dtheta):
    """Rotación inversa: velocidades del marco de referencia al robot."""
    c, s = math.cos(theta), math.sin(theta)
    return c * dx + s * dy, -s * dx + c * dy, dtheta


def inverse_kinematics(vx, vy, w):
    """Velocidades del chasis [m/s, m/s, rad/s] a ruedas [rad/s]."""
    lever = LX + LY
    return ((vx - vy - lever * w) / R,
            (vx + vy + lever * w) / R,
            (vx + vy - lever * w) / R,
            (vx - vy + lever * w) / R)


def forward_kinematics(w_fl, w_fr, w_rl, w_rr):
    """Velocidades medidas de las ruedas a velocidad corporal (odometría)."""
    return (R / 4 * (w_fl + w_fr + w_rl + w_rr),
            R / 4 * (-w_fl + w_fr + w_rl - w_rr),
            R / (4 * (LX + LY)) * (-w_fl + w_fr - w_rl + w_rr))
