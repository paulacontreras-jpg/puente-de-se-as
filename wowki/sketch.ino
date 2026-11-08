/*
  Puente de Señas - ESP32 en Wokwi
  Recibe mensajes por MQTT y los muestra en la LCD.
  Publica las respuestas rápidas de los botones.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.mqttdashboard.com";

// Tópicos
const char* TOPIC_SENAS     = "pau/puente/senas";
const char* TOPIC_MENSAJE   = "pau/puente/mensaje";
const char* TOPIC_RESPUESTA = "pau/puente/respuesta";  // ESP32 -> Streamlit (botones)

// Pines
const int PIN_LED = 2;
const int PIN_BUZZER = 18;
const int PIN_SI = 25;
const int PIN_NO = 26;
const int PIN_AYUDA = 27;

LiquidCrystal_I2C lcd(0x27, 16, 2);
WiFiClient espClient;
PubSubClient client(espClient);

// Para el desplazamiento de textos largos
String textoActual = "";
unsigned long ultimoScroll = 0;
int posScroll = 0;

unsigned long ultimoBoton = 0;

void beep(int ms) {
  unsigned long fin = millis() + ms;
  while (millis() < fin) {
    digitalWrite(PIN_BUZZER, HIGH);
    delayMicroseconds(500);
    digitalWrite(PIN_BUZZER, LOW);
    delayMicroseconds(500);
  }
}

void mostrar(const String& titulo, const String& texto) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(titulo.substring(0, 16));
  textoActual = texto;
  posScroll = 0;
  lcd.setCursor(0, 1);
  lcd.print(texto.substring(0, 16));
}

void actualizarScroll() {
  if (textoActual.length() <= 16) return;
  if (millis() - ultimoScroll < 400) return;
  ultimoScroll = millis();
  String ventana = textoActual + "   ";
  String vista = (ventana + ventana).substring(posScroll, posScroll + 16);
  lcd.setCursor(0, 1);
  lcd.print(vista);
  posScroll = (posScroll + 1) % ventana.length();
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  Serial.print(topic); Serial.print(" -> "); Serial.println(msg);

  if (String(topic) == TOPIC_SENAS) {
    mostrar("Sena:", msg);
  } else if (String(topic) == TOPIC_MENSAJE) {
    mostrar("Mensaje:", msg);
  }
  beep(200);
}

void setup_wifi() {
  Serial.print("Conectando a "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
}

void reconnect() {
  while (!client.connected()) {
    digitalWrite(PIN_LED, LOW);
    mostrar("Conectando MQTT", "...");
    String clientId = "PuenteSenas-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("MQTT conectado");
      client.subscribe(TOPIC_SENAS);
      client.subscribe(TOPIC_MENSAJE);
      digitalWrite(PIN_LED, HIGH);
      mostrar("Puente de Senas", "Listo");
    } else {
      Serial.print("falla, rc="); Serial.println(client.state());
      delay(3000);
    }
  }
}

void enviarRespuesta(const char* texto) {
  client.publish(TOPIC_RESPUESTA, texto);
  mostrar("Enviado:", texto);
  beep(80);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_SI, INPUT_PULLUP);
  pinMode(PIN_NO, INPUT_PULLUP);
  pinMode(PIN_AYUDA, INPUT_PULLUP);

  lcd.init();
  lcd.backlight();
  mostrar("Puente de Senas", "Iniciando...");

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  actualizarScroll();

  // Botones (activos en LOW) con pausa anti-rebote
  if (millis() - ultimoBoton > 300) {
    if (digitalRead(PIN_SI) == LOW)         { enviarRespuesta("SI");    ultimoBoton = millis(); }
    else if (digitalRead(PIN_NO) == LOW)    { enviarRespuesta("NO");    ultimoBoton = millis(); }
    else if (digitalRead(PIN_AYUDA) == LOW) { enviarRespuesta("AYUDA"); ultimoBoton = millis(); }
  }
}
