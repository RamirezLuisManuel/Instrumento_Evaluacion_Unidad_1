# Import para acceso a red
import network
# Para usar protocolo MQTT
from umqtt.simple import MQTTClient

# Importamos módulos necesarios
from machine import Pin
from time import sleep
from hcsr04 import HCSR04

# Propiedades para conectar a un cliente MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "utng/sensor"
MQTT_PORT = 1883

# Creo el objeto que me controlará el sensor
sensor = HCSR04(trigger_pin=15, echo_pin=4, echo_timeout_us=24000)

# Declaración de pines para los LEDs (simulando semáforo)
led_rojo = Pin(2, Pin.OUT)
led_azul1 = Pin(5, Pin.OUT)
led_azul2 = Pin(18, Pin.OUT)

# Apago todos los LEDs inicialmente
led_rojo.value(0)
led_azul1.value(0)
led_azul2.value(0)

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('raberry3', 'linux123')
    while not sta_if.isconnected():
        print(".", end="")
        sleep(0.3)
    print("WiFi Conectada!")

# Función para suscribir al broker MQTT
def subscribir():
    client = MQTTClient(MQTT_CLIENT_ID,
                        MQTT_BROKER, port=MQTT_PORT,
                        user=MQTT_USER,
                        password=MQTT_PASSWORD,
                        keepalive=0)
    client.set_callback(llegada_mensaje)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("Conectado a %s, en el topico %s" % (MQTT_BROKER, MQTT_TOPIC))
    return client

# Función encargada de controlar LEDs según el mensaje recibido
def llegada_mensaje(topic, msg):
    print("Mensaje:", msg)

# Control del semáforo según la distancia detectada
def controlar_leds(distancia):
    # Apaga todos los LEDs
    led_rojo.value(0)
    led_azul1.value(0)
    led_azul2.value(0)

    # Lógica del semáforo
    if distancia < 10:
        led_rojo.value(1)  # Distancia peligrosa (Rojo)
    elif 10 <= distancia < 20:
        led_azul1.value(1)  # Distancia moderada (Amarillo)
    else:
        led_azul2.value(1)  # Distancia segura (Verde)

# Conectar a WiFi
conectar_wifi()
# Subscripción a un broker MQTT
client = subscribir()

# Variable para almacenar la distancia anterior
distancia_anterior = 0

# Ciclo infinito
while True:
    client.check_msg()
    distancia = int(sensor.distance_cm())
    if distancia != distancia_anterior:
        print(f"La distancia es {distancia} cms.")
        client.publish(MQTT_TOPIC, str(distancia))
        controlar_leds(distancia)
    distancia_anterior = distancia
    sleep(2)
