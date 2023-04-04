#include <InverseK.h>

#include <InverseK.h>
#include <BraccioRobot.h>
#include <Servo.h>

#define GRIPPER_HALF_CLOSED 64
#define INPUT_SIZE 30
#define SPEED 30

Position testPosition(120, 120, 120, 120, 0,  GRIPPER_HALF_CLOSED);
Position myInitialPosition(90, 90, 90, 90, 90, GRIPPER_OPEN);

int numberFinalPosX[10] = {-250, -260, -270, -280, -290,
                            -300, -310, -320, -330, -340};
int numberFinalPosY[10] = {-250, -260, -270, -280, -290,
                            -300, -310, -320, -330, -340};

float x = -250;
float y = -200;
float z = 50;

void setup() {
  // Setup the lengths and rotation limits for each link
  float a0, a1, a2, a3;
  Serial.begin(9600);
  Link base, upperarm, forearm, hand;

  base.init(0, b2a(0.0), b2a(180.0));
  upperarm.init(200, b2a(15.0), b2a(165.0));
  forearm.init(200, b2a(0.0), b2a(180.0));
  hand.init(270, b2a(0.0), b2a(180.0));

  // Attach the links to the inverse kinematic model
  InverseK.attach(base, upperarm, forearm, hand);
  
  BraccioRobot.init();
  BraccioRobot.moveToPosition(myInitialPosition, 20);

  
}

// 200, 300
void loop() {
    int posx = -1, posy = -1;
    char input[INPUT_SIZE + 1];
    bool read = false;
    while(Serial.available() > 0){
      byte size = Serial.readBytes(input, INPUT_SIZE);
      input[INPUT_SIZE] = 0;
      read = true;
    }
    if(read){
      //int posxstart = map(atoi(strtok(input, " \n")), 0, 600, -300, 300);
      //int posystart = map(atoi(strtok(NULL, " \n")), 0, 600, -300, 300);
      int posxstart = atoi(strtok(input, " \n"));
      int posystart = atoi(strtok(NULL, " \n"));
      int angle = atoi(strtok(NULL, " \n"));
      //int posxstart = map(atoi(strtok(input, " \n")), -500, 500, -300, 300);
      //int posystart = map(atoi(strtok(NULL, " \n")), -500, 500, -300, 300);
      int posxfinish = atoi(strtok(NULL, " \n"));
      int posyfinish = atoi(strtok(NULL, " \n"));
      
      solveAndMoveRobot(posxstart, posystart, angle, posxfinish, posyfinish);
      read = false;
    }
}

void solveAndMoveRobot(int xStart, int yStart, int angle, int xFinish, int yFinish){
  float a0UP, a1UP, a2UP, a3UP;
  float a0DOWN, a1DOWN, a2DOWN, a3DOWN;

  bool goUP = false, goDOWN = false;

  goUP = InverseK.solve(xStart, yStart, 20, a0UP, a1UP, a2UP, a3UP);
  goDOWN = InverseK.solve(xFinish, yFinish, 50, a0DOWN, a1DOWN, a2DOWN, a3DOWN);

  if(goUP == false){
    Serial.print("ERROR_UP\n");
    return;
  }
  if(goDOWN == false){
    Serial.print("ERROR_DOWN\n");
    return;
  }
  moveRobotToPickUp(a0UP, a1UP, a2UP, a3UP, 20);
  moveRobotToDrop(a0DOWN, a1DOWN, a2DOWN, a3DOWN, angle);
  Serial.println("DONE\n");
}

void moveRobotToPickUp(float a0, float a1, float a2, float a3, float angle){
  testPosition.set(a2b(a0), 90, a2b(a2), 180, angle, 0);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
  testPosition.set(a2b(a0), a2b(a1) - 30, a2b(a2), 180, angle, 0);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
  testPosition.set(a2b(a0), a2b(a1) - 30, a2b(a2), 180, angle, 90);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
}

void moveRobotToDrop(float a0, float a1, float a2, float a3, float angle){
  testPosition.set(a2b(a0), a2b(a1) + 30, a2b(a2), a2b(a3), angle, 90);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
  testPosition.set(a2b(a0), a2b(a1) + 30, a2b(a2), a2b(a3), angle, 90);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
  testPosition.set(a2b(a0), a2b(a1) + 30, a2b(a2), a2b(a3), angle, 0);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
  testPosition.set(90, 60, 90, 90, 90, GRIPPER_OPEN);
  BraccioRobot.moveToPosition(testPosition, SPEED);
  delay(200);
}

// Quick conversion from the Braccio angle system to radians
float b2a(float b){
  return b / 180.0 * PI - HALF_PI;
}

// Quick conversion from radians to the Braccio angle system
float a2b(float a) {
  return (a + HALF_PI) * 180 / PI;
}
