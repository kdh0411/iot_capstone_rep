#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include "I2Cdev.h"
#include "MPU6050.h"
#include <math.h>
#include <SoftwareSerial.h>
#include <TinyGPS++.h>

// 지온 센서
#define ONE_WIRE_BUS 8
OneWire ourWire(ONE_WIRE_BUS);
DallasTemperature sensors(&ourWire);

// 토양 수분 센서 (A0 사용)
const int soilPin = A0;
int soilValue = 0;

// 기울기 센서 (MPU6050)
MPU6050 mpu;

// LoRa (D7 = RX, D6 = TX)
SoftwareSerial lora(6, 7); // RX, TX

// 5. GPS 모듈 설정 (SoftwareSerial 이용)
static const int GPS_RX_PIN = 4; // GPS 모듈의 TX핀과 연결될 아두이노 핀 (아두이노 RX)
static const int GPS_TX_PIN = 3; // GPS 모듈의 RX핀과 연결될 아두이노 핀 (아두이노 TX)
static const uint32_t GPS_BAUD = 9600; // GPS 모듈의 기본 통신 속도
TinyGPSPlus gps;               // TinyGPS++ 객체 생성
SoftwareSerial gpsSerial(GPS_RX_PIN, GPS_TX_PIN); // GPS용 SoftwareSerial 객체 생성


void setup() {
  Serial.begin(9600);
  lora.begin(115200);  // REYAX 기본 통신속도
  lora.println("AT+PARAMETER=11,7,1,4");  // 안정성과 길이 절충
  delay(200);

  // 지온 센서 초기화
  sensors.begin();

  // MPU6050 초기화
  Wire.begin();
  mpu.initialize();
  Serial.println("MPU6050 초기화 중...");
  if (mpu.testConnection()) {
    Serial.println("MPU6050 연결 성공!");
  } else {
    Serial.println("MPU6050 연결 실패 ㅠㅠ");
    while (1);
  }

  // --- GPS 모듈 초기화 ---
  gpsSerial.begin(GPS_BAUD);   // GPS 모듈과 시리얼 통신 시작
  Serial.println("GPS 모듈 초기화 완료. GPS 수신 대기 중...");

  
  // LoRa 설정
  delay(1000);
  lora.println("AT+ADDRESS=1");       // 이 보드 주소
  delay(200);
  lora.println("AT+NETWORKID=5");     // 네트워크 ID
  delay(200);
  lora.println("AT+BAND=915000000");  // 주파수 설정
  delay(200);

  Serial.println("LoRa 송신 시작!");
}

void loop() {
  // --- 1. GPS 데이터 읽기 및 파싱 ---
  while (gpsSerial.available() > 0) { // GPS 시리얼 데이터가 있으면
    gps.encode(gpsSerial.read());    // TinyGPS++ 라이브러리로 파싱
  }

  float latitude = 0.0;              // 위도 저장 변수
  float longitude = 0.0;             // 경도 저장 변수
  unsigned long gpsFixAge = 0;       // GPS Fix된 후 경과 시간 (밀리초)

  if (gps.location.isValid()) {      // GPS 위치 정보가 유효하면
    latitude = gps.location.lat();   // 위도 값 저장
    longitude = gps.location.lng();  // 경도 값 저장
    gpsFixAge = gps.location.age();  // GPS Fix 시간 정보 저장
  }

  // 토양 수분
  soilValue = analogRead(soilPin);

  // 지온
  sensors.requestTemperatures();
  float temperature = sensors.getTempCByIndex(0);

   // MPU6050: 가속도 + 자이로
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  
  float axf = ax / 16384.0;
  float ayf = ay / 16384.0;
  float azf = az / 16384.0;
  float gxf = gx / 131.0;
  float gyf = gy / 131.0;
  float gzf = gz / 131.0;
  
  float pitch = atan2(axf, sqrt(ayf * ayf + azf * azf)) * 180.0 / PI;
  float roll  = atan2(ayf, sqrt(axf * axf + azf * azf)) * 180.0 / PI;
  float A_mag = sqrt(axf * axf + ayf * ayf + azf * azf);
  float G_mag = sqrt(gxf * gxf + gyf * gyf + gzf * gzf);
  

  // 시리얼 출력
  Serial.print("Ax: "); Serial.print(ax);
  Serial.print(" Ay: "); Serial.print(ay);
  Serial.print(" Az: "); Serial.print(az);
  Serial.print(" Gx: "); Serial.print(gx);
  Serial.print(" Gy: "); Serial.print(gy);
  Serial.print(" Gz: "); Serial.println(gz);
  Serial.print("Pitch: "); Serial.print(pitch, 1);
  Serial.print(" deg\tRoll: "); Serial.print(roll, 1); Serial.println(" deg");
  Serial.print("Soil Moisture: "); Serial.println(soilValue);
  Serial.print("Temperature: "); Serial.print(temperature, 1); Serial.println(" C");

  // LoRa 전송 문자열 포맷
String data = 
  "a:" + String(A_mag) +
  ",g:" + String(G_mag) + 
  ",n:" + String(pitch, 1) + "," + String(roll, 1) +
  ",m:" + String(soilValue) +
  ",t:" + String(temperature, 1) +
  ",l:";

  if (gps.location.isValid()) { // GPS 위치가 유효하면 실제 값 사용
    data += String(latitude, 5) + "," + String(longitude, 5); // 위도, 경도 (소수점 6자리)
  } else { // GPS 위치가 유효하지 않으면 기본값 또는 오류 값 전송
    data += "0.00000,0.00000"; // 예: "0.0,0.0" (수신부에서 파싱 주의)
  }

  // 문자열 길이 구해서 전송
  int length = data.length();
  lora.print("AT+SEND=2,");
  lora.print(length);
  lora.print(",");
  lora.println(data);

  Serial.print("LoRa 전송: ");
  Serial.println(data);

  delay(1000);
}
