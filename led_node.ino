#include <SoftwareSerial.h>
#include <EEPROM.h>
#define LED_R 5
#define LED_G 6
#define LED_Y 7
#define EEPROM_DEV_ID_ADDR 0
#define EEPROM_CONN_FLAG_ADDR 1
#define EEPROM_UID_START 2
#define EEPROM_UID_LOW_START 2
#define EEPROM_UID_LOW_END 5
#define EEPROM_UID_MID_START 6
#define EEPROM_UID_MID_END 9
#define EEPROM_UID_HIGH_START 10
#define EEPROM_UID_HIGH_END 13
#define EEPROM_UID_END 13
#define BUTTON_PIN 10

unsigned char conn_flag;
unsigned char my_dev_id;
unsigned long U_ID[3] = {0, 0, 0};

SoftwareSerial XBee(2, 3);

void setup()
{
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_Y, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  digitalWrite(LED_R, LOW);
  digitalWrite(LED_G, LOW);
  digitalWrite(LED_Y, LOW);
  XBee.begin(9600);
  Serial.begin(9600);
  digitalWrite(LED_R, HIGH);
  delay(500);
  digitalWrite(LED_R, LOW);
  digitalWrite(LED_G, HIGH);
  delay(500);
  digitalWrite(LED_G, LOW);
  digitalWrite(LED_Y, HIGH);
  delay(500);
  digitalWrite(LED_Y, LOW);
  for (int i = 0; i <= 13; i++)
  {
    //EEPROM.update(i,0);
    //Serial.println(EEPROM.read(i));
  }
  while (XBee.available())
  {
    XBee.read();
  }
  my_dev_id = EEPROM.read(EEPROM_DEV_ID_ADDR);
  conn_flag = EEPROM.read(EEPROM_CONN_FLAG_ADDR);
  for (int k = 0; k < 3; k++)
  {
    for (int i = (EEPROM_UID_LOW_START + (k * 4)); i <= (EEPROM_UID_LOW_END + (k * 4)); i++)
    {
      //Serial.print(i);
      U_ID[2 - k] |= ((long)EEPROM.read(i) << (8 * (i - (EEPROM_UID_LOW_START + (k * 4)))));
    }
  }
  Serial.println(conn_flag);
  Serial.println(my_dev_id);
  for (int k = 0; k < 3; k++)
  {
    Serial.print(U_ID[k], HEX);
  }
}

void xbee_transmit(String data)
{
  int len = data.length();
  //Serial.print("Length: ");
  //Serial.println(len);
  XBee.write((len) | 0x30);
  for (int i = 0; i < len; i++)
  {
    XBee.write(data[i]);
    //Serial.print("Sent ");
    //Serial.println(data[i]);
  }
}

void xbee_transmit_status(String data)
{
  data = String(String(my_dev_id) + data);
  int length = data.length();
  XBee.write(length);
  for (int i = 0; i < length; i++)
  {
    XBee.write(data[i]);
    //Serial.print("Sent ");
    //Serial.println(data[i]);
  }
}

void connect_device()
{
  if((conn_flag == 0) && (digitalRead(BUTTON_PIN) == LOW))
  {
    
    while (XBee.available() < (EEPROM_UID_END - EEPROM_UID_START + 1));
    xbee_transmit("C");
    for (int k = 0; k < 3; k++)
    {
      for (int i = EEPROM_UID_LOW_START; i <= EEPROM_UID_LOW_END; i++)
      {
        unsigned char memory_store = XBee.read();
        EEPROM.update(i + k * 4, memory_store);
      }
    }
    for (int k = 0; k < 3; k++)
    {
      for (int i = (EEPROM_UID_LOW_START + (k * 4)); i <= (EEPROM_UID_LOW_END + (k * 4)); i++)
      {
        unsigned char shift = (i - (EEPROM_UID_LOW_START + (k * 4)));
        U_ID[2 - k] |= ((long)EEPROM.read(i) << (8 * shift));
      }
    }
    while (XBee.available() < 1);
    my_dev_id = XBee.read();
    EEPROM.update(EEPROM_DEV_ID_ADDR, my_dev_id);
    conn_flag = 1;
    EEPROM.update(EEPROM_CONN_FLAG_ADDR, conn_flag);
    for(int i = 0; i < 5; i++)
    {
      digitalWrite(5, HIGH);
      delay(100);
      digitalWrite(5, LOW);
      digitalWrite(6, HIGH);
      delay(100);
      digitalWrite(6, LOW);
      digitalWrite(7, HIGH);
      delay(100);
      digitalWrite(7,LOW);
    }
    for(int i = 0; i < 2; i++)
    {
      digitalWrite(5, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(7, HIGH);
      delay(400);
      digitalWrite(5, LOW);
      digitalWrite(6, LOW);
      digitalWrite(7,LOW);
      delay(200);
    }
  }
  else
  {
    while (XBee.available() < (EEPROM_UID_END - EEPROM_UID_START + 2));
    for (int i = 0; i < (EEPROM_UID_END - EEPROM_UID_START + 2); i++)
    {
      XBee.read();
    }
  }
}

void toggle_light()
{
  while (XBee.available() < EEPROM_UID_END - EEPROM_UID_START + 1);
  unsigned long U_ID_check[3] = {0, 0, 0};
  for (int k = 0; k < 3; k++)
  {
    for (int i = EEPROM_UID_LOW_START; i <= EEPROM_UID_LOW_END; i++)
    {
      U_ID_check[2 - k] |= (((long)XBee.read()) << 8 * (i - EEPROM_UID_START));
    }
  }
  //Serial.print("U_ID_check: ");
  //Serial.println(U_ID_check, HEX);
  if ((U_ID[0] == U_ID_check[0]) && (U_ID[1] == U_ID_check[1]) && (U_ID[2] == U_ID_check[2]))
  {
    //Serial.println("U_ID matches");
    while (XBee.available() < 1);
    unsigned int my_dev_id_check = XBee.read();
    if (my_dev_id == my_dev_id_check)
    {
      while (XBee.available() < 1);
      //Serial.println(color, HEX);
      unsigned char state = (XBee.read());
      //Serial.println(state, HEX);
      if (state & 0x04)
      {
        digitalWrite(5, HIGH);
      }
      else
      {
        digitalWrite(5, LOW);
      }
      if (state & 0x02)
      {
        digitalWrite(6, HIGH);
      }
      else
      {
        digitalWrite(6, LOW);
      }
      if (state & 0x01)
      {
        digitalWrite(7, HIGH);
      }
      else
      {
        digitalWrite(7, LOW);
      }
      xbee_transmit("C");
    }
    else
    {
      while (XBee.available() < 1);
      for (int i = 0; i < 1; i++)
      {
        XBee.read();
      }
    }
  }
  else
  {
    while (XBee.available() < (EEPROM_UID_END - EEPROM_UID_START + 1) + 2);
    for (int i = 0; i < (EEPROM_UID_END - EEPROM_UID_START + 1) + 2; i++)
    {
      XBee.read();
    }
  }
}

void light_all()
{
  while (XBee.available() < EEPROM_UID_END - EEPROM_UID_START + 1);
  unsigned long U_ID_check[3] = {0, 0, 0};
  for (int k = 0; k < 3; k++)
  {
    for (int i = EEPROM_UID_LOW_START; i <= EEPROM_UID_LOW_END; i++)
    {
      U_ID_check[2 - k] |= (((long)XBee.read()) << 8 * (i - EEPROM_UID_START));
    }
  }
  if ((U_ID[0] == U_ID_check[0]) && (U_ID[1] == U_ID_check[1]) && (U_ID[2] == U_ID_check[2]))
  {
    while (XBee.available() < 2);
    unsigned int state = XBee.read();
    unsigned char color = (XBee.read());
    //Serial.println(state, HEX);
    unsigned char affect = color & 0x4;
    if(affect)
    {
      if(affect & state)
      {
        digitalWrite(5, HIGH);
      }
      else
      {
        digitalWrite(5,LOW);
      }
    }
    affect = color & 0x2;
    if(affect)
    {
      if(affect & state)
      {
        digitalWrite(6, HIGH);
      }
      else
      {
        digitalWrite(6,LOW);
      }
    }
    affect = color & 0x1;
    if(affect)
    {
      if(affect & state)
      {
        digitalWrite(7, HIGH);
      }
      else
      {
        digitalWrite(7,LOW);
      }
    }
  }
  else
  {
    while (XBee.available() < 2);
    for (int i = 0; i < 2; i++)
    {
      XBee.read();
    }
  }
}

void disconnect_device()
{
  if(conn_flag == 1)
  {
    while (XBee.available() < EEPROM_UID_END - EEPROM_UID_START + 1);
    unsigned long U_ID_check[3] = {0, 0, 0};
    for (int k = 0; k < 3; k++)
    {
      for (int i = EEPROM_UID_LOW_START; i <= EEPROM_UID_LOW_END; i++)
      {
        U_ID_check[2 - k] |= (((long)XBee.read()) << 8 * (i - EEPROM_UID_START));
      }
    }
    //Serial.print("U_ID_check: ");
    //Serial.println(U_ID_check, HEX);
    if ((U_ID[0] == U_ID_check[0]) && (U_ID[1] == U_ID_check[1]) && (U_ID[2] == U_ID_check[2]))
    {
      //Serial.println("U_ID matches");
      while (XBee.available() < 1);
      unsigned int my_dev_id_check = XBee.read();
      if (my_dev_id == my_dev_id_check)
      {
        conn_flag = 0;
        EEPROM.update(EEPROM_CONN_FLAG_ADDR, conn_flag);
        xbee_transmit("D");
        for(int i = 0; i<2; i++)
        {
          digitalWrite(5, HIGH);
          digitalWrite(6, HIGH);
          digitalWrite(7, HIGH);
          delay(300);
          digitalWrite(5, LOW);
          digitalWrite(6, LOW);
          digitalWrite(7, LOW);
          delay(300);
        }
      }
    }
    else
    {
      while (XBee.available() < 1);
      XBee.read();
    }
  }
  else
  {
    while(XBee.available() < (EEPROM_UID_END - EEPROM_UID_START + 2));
    for (int i = 0; i < (EEPROM_UID_END - EEPROM_UID_START + 2); i++)
    {
      XBee.read();
    }
  }
}

void show()
{
  while (XBee.available() < EEPROM_UID_END - EEPROM_UID_START + 1);
  unsigned long U_ID_check[3] = {0, 0, 0};
  for (int k = 0; k < 3; k++)
  {
    for (int i = EEPROM_UID_LOW_START; i <= EEPROM_UID_LOW_END; i++)
    {
      U_ID_check[2 - k] |= (((long)XBee.read()) << 8 * (i - EEPROM_UID_START));
    }
  }
  if ((U_ID[0] == U_ID_check[0]) && (U_ID[1] == U_ID_check[1]) && (U_ID[2] == U_ID_check[2]))
  {
    while (XBee.available() < 2);
    unsigned int my_dev_id_check = XBee.read();
    unsigned char my_state = XBee.read();
    if (my_dev_id == my_dev_id_check)
    {
      xbee_transmit("S");
      delay(2000);
      for(int i = 0; i<5; i++)
      {
        digitalWrite(5, HIGH);
        digitalWrite(6, HIGH);
        digitalWrite(7, HIGH);
        delay(100);
        digitalWrite(5, LOW);
        digitalWrite(6, LOW);
        digitalWrite(7, LOW);
        delay(100);
        digitalWrite(5, HIGH);
        digitalWrite(6, HIGH);
        digitalWrite(7, HIGH);
        delay(100);
        digitalWrite(5, LOW);
        digitalWrite(6, LOW);
        digitalWrite(7, LOW);
        delay(200);
      }
      if(my_state & 0x04)
      {
        digitalWrite(5, HIGH);
      }
      if(my_state & 0x02)
      {
        digitalWrite(6,HIGH);
      }
      if(my_state & 0x01)
      {
        digitalWrite(7, HIGH);
      }
    }
  }
  else
  {
    while (XBee.available() < 2);
    for(int i = 0; i<2; i++)
    {
      XBee.read();
    }
  }
}

void loop()
{
  while (XBee.read() != 0x7e);
  //Serial.println("Ready for mode");
  while (XBee.available() < 1);
  char mode = XBee.read();
  //Serial.print("Mode: ");
  //Serial.println(mode);
  switch (mode)
  {
    case 'C': connect_device();
      Serial.println("Ready");
      break;
    case 'L': toggle_light();
      Serial.println("Ready");
      break;
    case 'D': disconnect_device();
      Serial.println("Ready");
      break;
    case 'A': light_all();
      break;
    case 'S': show();
      break;
    default:  Serial.println("Command not found!");
      break;
  }
  
}
