#include <SPI.h>
#include <Wire.h>

#include <BaseNode.h>

#include "ElectromagnetController.h"

void setup() {
  ElectromagnetController.begin();
}
void loop() {
  ElectromagnetController.listen();
}
