#include "ElectromagnetController.h"
#include "Config.h"

#define P(str) (strcpy_P(p_buffer_, PSTR(str)), p_buffer_)

ElectromagnetControllerClass ElectromagnetController;

const char BaseNode::PROTOCOL_NAME_[] PROGMEM = "DropBot protocol";
const char BaseNode::PROTOCOL_VERSION_[] PROGMEM = "0.1";
const char BaseNode::MANUFACTURER_[] PROGMEM = "Wheeler Microfluidics Lab";
const char BaseNode::NAME_[] PROGMEM = "Electromagnet controller";
const char BaseNode::HARDWARE_VERSION_[] PROGMEM = ___HARDWARE_VERSION___;
const char BaseNode::SOFTWARE_VERSION_[] PROGMEM = ___SOFTWARE_VERSION___;
const char BaseNode::URL_[] PROGMEM = "http://microfluidics.utoronto.ca/dropbot";


ElectromagnetControllerClass::ElectromagnetControllerClass() {
  power_ = 255;
  state_ = OFF;
}

void ElectromagnetControllerClass::process_wire_command() {
  switch (cmd_) {
  case CMD_SET_POWER:
    if(payload_length_ == sizeof(uint8_t)) {
      set_power(read<uint8_t>());
      return_code_ = RETURN_OK;
    } else {
      return_code_ = RETURN_BAD_PACKET_SIZE;
    }
    break;
  case CMD_GET_POWER:
    if(payload_length_ == 0) {
      serialize(&power_, sizeof(power_));
      return_code_ = RETURN_OK;
    } else {
      return_code_ = RETURN_BAD_PACKET_SIZE;
    }
    break;
  case CMD_SET_STATE:
    if(payload_length_ == sizeof(uint8_t)) {
      return_code_ = set_state(read<uint8_t>());
    } else {
      return_code_ = RETURN_BAD_PACKET_SIZE;
    }
    break;
  case CMD_GET_STATE:
    if(payload_length_ == 0) {
      serialize(&state_, sizeof(state_));
      return_code_ = RETURN_OK;
    } else {
      return_code_ = RETURN_BAD_PACKET_SIZE;
    }
    break;
  case CMD_GET_CURRENT:
    if(payload_length_ == 0) {
      uint16_t current = get_current();
      serialize(&current, sizeof(current));
      return_code_ = RETURN_OK;
    } else {
      return_code_ = RETURN_BAD_PACKET_SIZE;
    }
    break;
  default:
    BaseNode::process_wire_command();
    break;
  }
}

/* If there is a request pending on the serial port, process it. */
bool ElectromagnetControllerClass::process_serial_input() {
  if (match_function(P("off()"))) {
    set_state(OFF);
    return true;
  } else if (match_function(P("on()"))) {
    set_state(ON);
    return true;
  } else if (match_function(P("forward()"))) {
    set_state(FORWARD);
    return true;
  } else if (match_function(P("reverse()"))) {
    set_state(REVERSE);
    return true;
  } else if (match_function(P("power()"))) {
    Serial.println("power=" + String(power_));
    return true;
  } else if (match_function(P("state()"))) {
    if (state_==OFF) {
      Serial.println("state=OFF");
    } else if (state_==ON) {
      Serial.println("state=ON");
    } else if (state_==FORWARD) {
      Serial.println("state=FORWARD");
    } else if (state_==REVERSE) {
      Serial.println("state=REVERSE");
    }
    return true;
  } else if (match_function(P("set_power("))) {
    int32_t value;
    if (read_int(value)) {
      set_power(value);
    }
    return true;
  }

  /* If we haven't processed the command, let the BaseNode process it. */
  return BaseNode::process_serial_input();
}

void ElectromagnetControllerClass::set_power(uint8_t power) {
  power_ = power;
  analogWrite(PIN_PWM, power_);
  Serial.print("power=");
  Serial.println(power_);
}

uint8_t ElectromagnetControllerClass::set_state(uint8_t state) {
  if (state==OFF) {
    digitalWrite(PIN_IN_A, LOW);
    digitalWrite(PIN_IN_B, LOW);
    Serial.println("state=OFF");
  } else if (state==ON) {
    digitalWrite(PIN_IN_A, HIGH);
    digitalWrite(PIN_IN_B, HIGH);
    Serial.println("state=ON");
  } else if (state==FORWARD) {
    digitalWrite(PIN_IN_A, HIGH);
    digitalWrite(PIN_IN_B, LOW);
    Serial.println("state=FORWARD");
  } else if (state==REVERSE) {
    digitalWrite(PIN_IN_A, LOW);
    digitalWrite(PIN_IN_B, HIGH);
    Serial.println("state=REVERSE");
  } else {
    return RETURN_BAD_VALUE;
  }
  // if we get here, everything is ok
  state_ = state;
  return RETURN_OK;
}

uint16_t ElectromagnetControllerClass::get_current() {
  uint16_t current = analogRead(PIN_CS);
  Serial.println("current=" + String(current));
  return current;
}

void ElectromagnetControllerClass::begin() {
  BaseNode::begin();
  pinMode(PIN_PWM, OUTPUT);
  pinMode(PIN_IN_A, OUTPUT);
  pinMode(PIN_IN_B, OUTPUT);
  set_state(state_);
  set_power(power_);
}

void ElectromagnetControllerClass::listen() {
  BaseNode::listen();
}
