import rospy
from turtlesim.msg import Pose
from std_msgs.msg import String

class Turtle:
    def __init__(self, name, x=0, y=0, radius=1):
        self.name = name
        self.x = x
        self.y = y
        self.health = 100
        self.attacks_left = 10
        self.radius = radius  #turtle's radius

    def apply_damage(self):
        self.health -= 10
        if self.health < 0:
            self.health = 0



class GameEngine:
    def __init__(self):
        rospy.init_node('game_engine')

        self.max_turtles = 7
        self.turtles = []
        self.game_over = False
        self.winner = None
        self.collision_damage = 10  # damage amount for each collision

        
        for i in range(self.max_turtles):
            self.pose_subscriber = rospy.Subscriber('/turtle1/pose', Pose, self.update_pose)
            self.pose_subscriber = rospy.Subscriber('/spawns', String, self.create_turtle)
            self.pose_subscriber = rospy.Subscriber('/attacks', String, self.handle_attack)




        self.pose = Pose()
        self.rate = rospy.Rate(10)
        
        pub = rospy.Publisher('game_logic', String, queue_size=10)
        self.publish_game_start_message()


        rospy.spin()  # for the node to keep running and processing incoming messages throughout the game


    def publish_game_start_message(self):
        msg = String()
        msg.data = "Turtles' Battle Begin"
        self.pub.publish(msg)

    def add_default_turtle(self):
        default_name = "Turtle_1"
        default_turtle = Turtle(name=default_name, x=0, y=0)
        self.turtles.append(default_turtle)
        rospy.loginfo(f"Added default turtle: {default_turtle.name} at position ({default_turtle.x}, {default_turtle.y})")


    def create_turtle(self, msg):
        if len(self.turtles) > 7:
            rospy.logwarn("Maximum number of turtles reached can't add more!")
            return
        
        # Create a new turtle from the message data
        new_turtle = Turtle(name=msg.name, x=0, y=0)
        self.turtles.append(new_turtle)
        rospy.loginfo(f"Added new turtle: {new_turtle.name} at position ({new_turtle.x}, {new_turtle.y})")

   
    def update_pose(self, data):
        self.pose = data
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)

    
    def handle_attack(self, msg):
        attacker_name = msg.attacker_name
        attacker_x = msg.attacker_x
        attacker_y = msg.attacker_y

        # Find the attacker turtle by name
        attacker = next((t for t in self.turtles if t.name == attacker_name), None)
        if attacker is None:
            rospy.logwarn(f"Attacker turtle with name {attacker_name} not found.")
            return

        # Update the attacker position
        attacker.update_position(attacker_x, attacker_y)

        # Check distance and apply damage
        for turtle in self.turtles:
            if turtle.name != attacker_name:  # Skip the attacker itself
                distance = ((attacker.x - turtle.x) ** 2 + (attacker.y - turtle.y) ** 2) ** 0.5
                if distance < (attacker.radius + turtle.radius):  # Check if within attack range
                    self.apply_damage(attacker, turtle)
                    rospy.loginfo(f"{attacker.name} attacked {turtle.name}!")


    def apply_damage(self, attacker, defender):
        if attacker.attacks_left > 0:
            defender.apply_damage(self.collision_damage)
            attacker.attacks_left -= 1

    def check_game_over(self):
        if all(turtle.attacks_left == 0 for turtle in self.turtles):
            self.game_over = True
            winner_index = max(range(len(self.turtles)), key=lambda i: self.turtles[i].health)
            self.winner = self.turtles[winner_index].name
            rospy.loginfo(f"Game Over! Winner: {self.winner}")
            msg = String()
            msg.data = f"Game Over! Winner: {self.winner}"
            self.pub.publish(msg)

    def game_loop(self):
      while not rospy.is_shutdown() and not self.game_over:
        self.check_game_over()
        self.rate.sleep()



def main():
    game_engine = GameEngine()
    game_engine.add_default_turtle()
    game_engine.game_loop()

if __name__ == '__main__':
    main()