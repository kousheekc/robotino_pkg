#include "rto_node/MotorArrayROS.hpp"

MotorArrayROS::MotorArrayROS(rclcpp::Node* node) : node_(node)
{
	motor_pub_ = node_->create_publisher<rto_msgs::msg::MotorReadings>("motor_readings", 10);
}

MotorArrayROS::~MotorArrayROS()
{
}

void MotorArrayROS::getMotorReadings(std::vector<float> &velocities, std::vector<int> &positions)
{
	velocities = motor_msg_.velocities;
	positions = motor_msg_.positions;
}

void MotorArrayROS::velocitiesChangedEvent(const float* velocities, unsigned int size)
{
	// Build the MotorReadings msg
	motor_msg_.velocities.resize(size, 0.0);

	if(velocities != NULL)
	{
		memcpy(motor_msg_.velocities.data(), velocities, size * sizeof(float));
	}
}

void MotorArrayROS::positionsChangedEvent(const int* positions, unsigned int size)
{
	// Build the MotorReadings msg
	motor_msg_.positions.resize(size, 0.0);

	if(positions != NULL)
	{
		memcpy(motor_msg_.positions.data(), positions, size * sizeof(int));
	}
}

void MotorArrayROS::currentsChangedEvent(const float* currents, unsigned int size)
{
	// Build the MotorReadings msg
	motor_msg_.header.stamp = node_->now();
	motor_msg_.currents.resize(size);

	if(currents != NULL)
	{
		memcpy(motor_msg_.currents.data(), currents, size * sizeof(float));
	}

	// Publish the msg
	motor_pub_->publish(motor_msg_);
}