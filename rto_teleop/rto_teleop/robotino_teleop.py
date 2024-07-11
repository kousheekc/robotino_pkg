import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from rto_msgs.msg import DigitalReadings

class Robotino3Teleop(Node):

    def __init__(self):
        super().__init__('robotino_joyteleop', namespace='')
        
        # create subscription to joy topic
        self.subscription = self.create_subscription(Joy, 'joy', self.TeleopCallback, 10)
        
        # create publishers
        self.cmd_vel_publisher= self.create_publisher(Twist, 'cmd_vel_joy', 10)
        self.gripper_publisher= self.create_publisher(DigitalReadings, 'set_digital_values', 10)
        
        # Initialize parameters
        self.declare_parameter('forward_axis_scalling', 1.0)
        self.declare_parameter('angular_axis_scalling', 1.0)
        self.declare_parameter('deadzone', 0.1)
        self.declare_parameter('x_axis', 3)
        self.declare_parameter('y_axis', 2)
        self.declare_parameter('w_axis', 0)
        self.declare_parameter('grip_button', 4)
        self.declare_parameter('drop_button', 5)
        
    # callback function to publish data over cmd_vel topic based on joy_pad inputs
    def TeleopCallback(self, data: Joy):
        if (data.buttons[self.get_parameter('grip_button').value] == 1):
            grip_msg = DigitalReadings()
            grip_msg.header.stamp = self.get_clock().now().to_msg()
            grip_msg.values = [False] * 8
            grip_msg.values[7] = True
            self.gripper_publisher.publish(grip_msg)
        if (data.buttons[self.get_parameter('drop_button').value] == 1):
            grip_msg = DigitalReadings()
            grip_msg.header.stamp = self.get_clock().now().to_msg()
            grip_msg.values = [False] * 8
            grip_msg.values[7] = False
            self.gripper_publisher.publish(grip_msg)

        f_scale = self.get_parameter('forward_axis_scalling').value
        z_scale = self.get_parameter('angular_axis_scalling').value

        x = data.axes[self.get_parameter('x_axis').value]*f_scale
        y = data.axes[self.get_parameter('y_axis').value]*f_scale
        w = data.axes[self.get_parameter('w_axis').value]*z_scale

        if (abs(x) < self.get_parameter('deadzone').value):
            x = 0.0
        if (abs(y) < self.get_parameter('deadzone').value):
            y = 0.0
        if (abs(w) < self.get_parameter('deadzone').value):
            w = 0.0

        if (x == 0.0 and y == 0.0 and w == 0.0):
            return
        
        p_msg = Twist()

        p_msg.linear.x = x
        p_msg.linear.y = y
        p_msg.linear.z = 0.0
        
        p_msg.angular.x = 0.0
        p_msg.angular.y = 0.0
        p_msg.angular.z = w

        self.cmd_vel_publisher.publish(p_msg)

def main():
    rclpy.init()
    teleop_node = Robotino3Teleop()
    try:
        rclpy.spin(teleop_node)
    except KeyboardInterrupt:
        pass
    teleop_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
