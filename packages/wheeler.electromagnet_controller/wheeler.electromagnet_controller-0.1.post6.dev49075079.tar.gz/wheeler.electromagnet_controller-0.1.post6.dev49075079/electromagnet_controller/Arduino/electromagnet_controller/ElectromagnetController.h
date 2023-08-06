#ifndef ___ELECTROMAGNET_CONTROLLER__H___
#define ___ELECTROMAGNET_CONTROLLER__H___

#include <BaseNode.h>

class ElectromagnetControllerClass : public BaseNode {
public:
  // digital pins
  static const uint8_t PIN_IN_A = 8;
  static const uint8_t PIN_IN_B = 6;
  static const uint8_t PIN_PWM = 5;

  // analog pins
  static const uint8_t PIN_CS = 0; // A0
  
  // state definitions
  static const uint8_t OFF = 0;
  static const uint8_t ON = 1;
  static const uint8_t FORWARD = 2;
  static const uint8_t REVERSE = 3;
  
  // command codes
  static const uint8_t CMD_SET_POWER =       0xA0;
  static const uint8_t CMD_GET_POWER =       0xA1;
  static const uint8_t CMD_SET_STATE =       0xA2;
  static const uint8_t CMD_GET_STATE =       0xA3;
  static const uint8_t CMD_GET_CURRENT =     0xA4;

  ElectromagnetControllerClass();
  void begin();
  void listen();
  void process_wire_command();
  bool process_serial_input();
  
private:
  void set_power(uint8_t power);
  uint8_t set_state(uint8_t state);
  uint16_t get_current();
  
  uint8_t power_;
  uint8_t state_;
};

extern ElectromagnetControllerClass ElectromagnetController;

#endif // ___ELECTROMAGNET_CONTROLLER__H___
