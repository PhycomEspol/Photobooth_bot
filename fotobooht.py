import smtplib
from email.message import EmailMessage
import time
import cv2
import mediapipe as mp
import numpy as np
import math
from math import acos, degrees
from PIL import Image
#1. codigo de foto
info = []

def palm_centroid(coordinates_list):
    coordinates = np.array(coordinates_list)
    centroid = np.mean(coordinates, axis=0)
    centroid = int(centroid[0]), int(centroid[1])
    return centroid
def agg_marco(foto,marco,nombre):
    img=Image.open(foto)
    fondo=Image.open(marco)
    img_re=img.resize((258,328))
    fondo_re = fondo.resize((425, 350))

    # Crear una máscara a partir de la imagen png
    mask = fondo_re.convert("RGBA").split()[-1]

    # Combinar imágenes usando la máscara
    img_re.paste(fondo_re, (-85, -10), mask)

    img_re.show()
    img_re.save(f'C:\\Users\\nahom\\Downloads\\{nombre}.jpg')
    return f'C:\\Users\\nahom\\Downloads\\{nombre}.jpg'

def enviar_correo(info,nombre):
    for b, c in info:
        destinatario = c
        asunto = 'UN RECUERDO CON PHYCOM!'
        mensaje = ''''¡Hola a todos! Soy Phybot, el bot del club. ¡Bienvenidos a Espol! 😊 \n
        Quería tomar un momento para agradecerles por usar el photobooth y unirse a nuestra comunidad. Espero que hayan disfrutado de su experiencia y que hayan capturado algunos momentos divertidos y especiales. \n
        Les doy la bienvenida a todos a Espol y les animo a involucrarse en todo lo que la universidad tiene para ofrecer. \n
        Desde clubs y organizaciones estudiantiles hasta eventos y actividades en el campus, hay muchas maneras de conocer gente nueva y hacer amigos. \n
        Les deseo mucho éxito en su tiempo aquí en Espol y espero que disfruten de todo lo que la universidad tiene para ofrecer.'''

    # Crea el cuerpo del correo electrónico
    cuerpo = EmailMessage()
    cuerpo['From'] = 'phycomespol2018@gmail.com'
    cuerpo['To'] = destinatario
    cuerpo['Subject'] = asunto
    cuerpo.set_content(mensaje)

    # Agrega las fotos como archivos adjuntos

    for b, c in info:
        if nombre in b:
            with open(b, 'rb') as archivo:
                cuerpo.add_attachment(archivo.read(), maintype='image', subtype='jpeg', filename=b)

    # Envía el correo electrónico
    with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
        servidor.starttls()
        servidor.login('phycomespol2018@gmail.com', 'gevenfatripvsxuf')
        servidor.send_message(cuerpo)
    return True





mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(2)
envio=''
while envio!= True:
    correo = input('ingrese su correo electronico: ')
    nombre = input('ingrese su nombre: ')
    # Pulgar
    thumb_points = [1, 2, 4]

    # Índice, medio, anular y meñique
    palm_points = [0, 1, 2, 5, 9, 13, 17]
    fingertips_points = [8, 12, 16, 20]
    finger_base_points = [6, 10, 14, 18]

    # Colores
    GREEN = (48, 255, 48)
    BLUE = (192, 101, 21)
    YELLOW = (0, 204, 255)
    PURPLE = (128, 64, 128)
    PEACH = (180, 229, 255)

    with mp_hands.Hands(
            model_complexity=1,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
        while True:
            ret, frame = cap.read()
            if ret == False:
                break
            frame1 = cv2.flip(frame, 1)
            height, width, _ = frame1.shape
            frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            fingers_counter = "_"
            thickness = [2, 2, 2, 2, 2]

            if results.multi_hand_landmarks:
                coordinates_thumb = []
                coordinates_palm = []
                coordinates_ft = []
                coordinates_fb = []
                for hand_landmarks in results.multi_hand_landmarks:
                    for index in thumb_points:
                        x = int(hand_landmarks.landmark[index].x * width)
                        y = int(hand_landmarks.landmark[index].y * height)
                        coordinates_thumb.append([x, y])

                    for index in palm_points:
                        x = int(hand_landmarks.landmark[index].x * width)
                        y = int(hand_landmarks.landmark[index].y * height)
                        coordinates_palm.append([x, y])

                    for index in fingertips_points:
                        x = int(hand_landmarks.landmark[index].x * width)
                        y = int(hand_landmarks.landmark[index].y * height)
                        coordinates_ft.append([x, y])

                    for index in finger_base_points:
                        x = int(hand_landmarks.landmark[index].x * width)
                        y = int(hand_landmarks.landmark[index].y * height)
                        coordinates_fb.append([x, y])
                    ##########################
                    # Pulgar
                    p1 = np.array(coordinates_thumb[0])
                    p2 = np.array(coordinates_thumb[1])
                    p3 = np.array(coordinates_thumb[2])

                    l1 = np.linalg.norm(p2 - p3)
                    l2 = np.linalg.norm(p1 - p3)
                    l3 = np.linalg.norm(p1 - p2)

                    # Calcular el ángulo
                    angle = math.degrees(acos((l1 ** 2 + l3 ** 2 - l2 ** 2) / (2 * l1 * l3)))
                    thumb_finger = np.array(False)
                    if angle > 150:
                        thumb_finger = np.array(True)

                    ################################
                    # Índice, medio, anular y meñique
                    nx, ny = palm_centroid(coordinates_palm)
                    cv2.circle(frame1, (nx, ny), 3, (0, 255, 0), 2)
                    coordinates_centroid = np.array([nx, ny])
                    coordinates_ft = np.array(coordinates_ft)
                    coordinates_fb = np.array(coordinates_fb)

                    # Distancias
                    d_centrid_ft = np.linalg.norm(coordinates_centroid - coordinates_ft, axis=1)
                    d_centrid_fb = np.linalg.norm(coordinates_centroid - coordinates_fb, axis=1)
                    dif = d_centrid_ft - d_centrid_fb
                    fingers = dif > 0
                    fingers = np.append(thumb_finger, fingers)
                    fingers_counter = str(np.count_nonzero(fingers == True))
                    for (i, finger) in enumerate(fingers):
                        if finger == True:
                            thickness[i] = -1
                    mp_drawing.draw_landmarks(
                        frame1,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    ################################
            if fingers_counter == '2':
                cv2.putText(frame1, 'tomando foto', (255, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                time.sleep(3)
                cv2.putText(frame1, 'foto tomada', (255, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                booth = cv2.imwrite(f'C:\\Users\\nahom\\Downloads\\induccion novatos 2023\\{nombre}.jpg', frame)
                #2. edicion
                final=agg_marco(f'C:\\Users\\nahom\\Downloads\\induccion novatos 2023\\{nombre}.jpg','marco.png',nombre)

                info.append(tuple([final, correo]))
                envio=enviar_correo(info,nombre)
                print(envio)
                correo = input('ingrese su correo de gmail:')
                nombre = input('ingrese su nombre: ')
            cv2.imshow("Frame", frame1)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    cap.release()
    cv2.destroyAllWindows()



 


