/*
    This sketch shows how to handle HTTP Digest Authorization.

    Written by Parham Alvani and Sajjad Rahnama, 2018-01-07.

   This example is released into public domain,
   or, at your option, CC0 licensed.

Fichier -> préférence, ajouter dans "URL de gestionnaire de cartes supplémentaire" l'url suivante :
    http://arduino.esp8266.com/stable/package_esp8266com_index.json
Dans Outils -> type de carte -> Gestionnaire de carte chercher esp8266 et installer le machin
Dans Outils -> type de carte sélectionner Generic ESP8266 Module

Pour flasher le module, il faut que la GPIO0 soit au niveau bas au démarrage (ou reset) du module
à voir : https://www.fais-le-toi-meme.fr/fr/electronique/tutoriel/esp8266-arduinoota-mise-a-jour-logiciel-esp8266-wifi

 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


int ledPin = 2;
int buttonPin = 0;

// Variables will change:
int ledState = LOW;         // the current state of the output pin
int buttonState;             // the current reading from the input pin
int lastButtonState = HIGH;   // the previous reading from the input pin

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers

unsigned long start_recording_time = 0;
const unsigned long AUTO_STOP_TIME = 300000;  //300s = 5min
const unsigned long AUTO_STOP_WARNING_TIME = 270000;  //270s = 4min30s
unsigned long last_blink_time = 0;
unsigned long last_check_time = 0;
const unsigned long CHECK_TIME = 60000; //60s = 1min
int blinkState = ledState;

const char* ssid = "pprz_router";

const char *username = "root";
const char *password = "vtoenacpprz";

const char *server = "http://192.168.1.232/";
const char *uri_check = "/axis-cgi/io/port.cgi?check=2";
const char *uri_start_recording = "/axis-cgi/io/virtualinput.cgi?action=1:/";
const char *uri_stop_recording = "/axis-cgi/io/virtualinput.cgi?action=1:%5c";

String exractParam(String& authReq, const String& param, const char delimit) {
  int _begin = authReq.indexOf(param);
  if (_begin == -1) {
    return "";
  }
  return authReq.substring(_begin + param.length(), authReq.indexOf(delimit, _begin + param.length()));
}

String getCNonce(const int len) {
  static const char alphanum[] =
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz";
  String s = "";

  for (int i = 0; i < len; ++i) {
    s += alphanum[rand() % (sizeof(alphanum) - 1)];
  }

  return s;
}

String getDigestAuth(String& authReq, const String& username, const String& password, const String& uri, unsigned int counter) {
  // extracting required parameters for RFC 2069 simpler Digest
  String realm = exractParam(authReq, "realm=\"", '"');
  String nonce = exractParam(authReq, "nonce=\"", '"');
  String cNonce = getCNonce(8);

  char nc[9];
  snprintf(nc, sizeof(nc), "%08x", counter);

  // parameters for the RFC 2617 newer Digest
  MD5Builder md5;
  md5.begin();
  md5.add(username + ":" + realm + ":" + password);  // md5 of the user:realm:user
  md5.calculate();
  String h1 = md5.toString();

  md5.begin();
  md5.add(String("GET:") + uri);
  md5.calculate();
  String h2 = md5.toString();

  md5.begin();
  md5.add(h1 + ":" + nonce + ":" + String(nc) + ":" + cNonce + ":" + "auth" + ":" + h2);
  md5.calculate();
  String response = md5.toString();

  String authorization = "Digest username=\"" + username + "\", realm=\"" + realm + "\", nonce=\"" + nonce +
                         "\", uri=\"" + uri + "\", algorithm=\"MD5\", qop=auth, nc=" + String(nc) + ", cnonce=\"" + cNonce + "\", response=\"" + response + "\"";
  Serial.println(authorization);

  return authorization;
}


int send_digest_request(const char *uri, char* answer, unsigned int len) {
  int return_status = 0;
  
  HTTPClient http;

  Serial.print("[HTTP] begin...\n");

  // configure traged server and url
  http.begin(String(server) + String(uri));


  const char *keys[] = {"WWW-Authenticate"};
  http.collectHeaders(keys, 1);

  Serial.print("[HTTP] GET...\n");
  // start connection and send HTTP header
  int httpCode = http.GET();

  if (httpCode > 0) {
    String authReq = http.header("WWW-Authenticate");
    Serial.println(authReq);
  http.end();

  while(http.connected()) {
    delay(10);
    http.end();
  }
    String authorization = getDigestAuth(authReq, String(username), String(password), String(uri), 1);

    http.begin(String(server) + String(uri));

    http.addHeader("Authorization", authorization);

    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println(payload);
      payload.toCharArray(answer, len);
    } else {
      Serial.printf("[HTTP] Auth GET failed: %s\n", http.errorToString(httpCode).c_str());
      return_status = -1;
    }
  } else {
    Serial.printf("[HTTP] initial request failed: %s\n", http.errorToString(httpCode).c_str());
    return_status = -2;
  }

  http.end();

  return return_status;
}

void setup() {
  Serial.begin(115200);
  
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP); 
  digitalWrite(ledPin, ledState);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    blinkState = !blinkState;
    digitalWrite(ledPin, blinkState);
    delay(200);
    Serial.print(".");
  }
  digitalWrite(ledPin, ledState);

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {

  // Almost end of the recording, lets warn the user !
  if(ledState && (millis() - start_recording_time) > AUTO_STOP_WARNING_TIME) {
    if((millis() - last_blink_time)> 1000) {
      blinkState = !blinkState;
      digitalWrite(ledPin, blinkState);
      last_blink_time = millis();
    }
  }

  // Overtime ! Lets stop the recording.
  if(ledState && (millis() - start_recording_time) > AUTO_STOP_TIME) {
    while(send_digest_request(uri_stop_recording, NULL, 0)) { //If error, lets try again !
      delay(5000);
    }
    ledState = 0;
    digitalWrite(ledPin, ledState);
    //start_recording_time = 0;
  }


  //lets check if the camera is in the expected state !
  if(millis() - last_check_time > CHECK_TIME) {
    char response[50] = "";
    while(send_digest_request(uri_check, response, 50)) { //If error, lets try again !
      Serial.println("request failed, try again in 5s...");
      delay(5000);
    }
    int d_answer;
    sscanf(response, "port2=%d", &d_answer);
    if(ledState) {
      if(d_answer == 0) { //expected 1 got 0
        while(send_digest_request(uri_start_recording, NULL, 0)) { //If error, lets try again !
          delay(5000);
        }
      }
    } else {
      if(d_answer == 1) { //expected 0 got 1
        while(send_digest_request(uri_stop_recording, NULL, 0)) { //If error, lets try again !
          delay(5000);
        }
      }
    }
    last_check_time = millis();
  }





  
  // read the state of the switch into a local variable:
  int reading = digitalRead(buttonPin);

  // check to see if you just pressed the button
  // (i.e. the input went from LOW to HIGH), and you've waited long enough
  // since the last press to ignore any noise:

  // If the switch changed, due to noise or pressing:
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer than the debounce
    // delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState) {
      buttonState = reading;

      // only toggle the LED if the new button state is LOW
      if (buttonState == LOW) {
        //WARNING period : just reset the timer !
        if(ledState && (millis() - start_recording_time) > AUTO_STOP_WARNING_TIME) {
           start_recording_time = millis();
           digitalWrite(ledPin, ledState);
           return;  // do not switch off !
        }


        
        ledState = !ledState;
        digitalWrite(ledPin, ledState);

        if(ledState) {  //start recording
          while(send_digest_request(uri_start_recording, NULL, 0)) { //If error, lets try again !
            delay(5000);
          }
          start_recording_time = millis();
        } else {    //stop recording
          while(send_digest_request(uri_stop_recording, NULL, 0)) { //If error, lets try again !
            delay(5000);
          }
        }

        
      }
    }
  }

  // set the LED:
  

  // save the reading. Next time through the loop, it'll be the lastButtonState:
  lastButtonState = reading;
}
