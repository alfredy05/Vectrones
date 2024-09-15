import os
import cv2
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from deepface import DeepFace

# Creación de la ventana principal
root = Tk()
root.title("BANORTE")
root.geometry("360x640")  # Resolución móvil
root.config(bg="lightgrey", cursor="circle")

# Variables de usuario
nombre = StringVar()
apellido = StringVar()
correo = StringVar()
telefono = StringVar()
file_path = None  # Variable para almacenar la ruta del archivo cargado

# Función para cambiar de pantalla
def mostrar_frame(frame):
    frame.tkraise()

# Función para guardar datos en un archivo de texto
def guardar_datos():
    with open("datos_usuario.txt", "w") as file:
        file.write(f"Nombre(s): {nombre.get()}\n")
        file.write(f"Apellido(s): {apellido.get()}\n")
        file.write(f"Correo: {correo.get()}\n")
        file.write(f"Teléfono: {telefono.get()}\n")

# Pantalla inicial: Nombre y Apellido
def pantalla_1():
    global frame1
    frame1 = Frame(root, bg="lightgrey")
    frame1.place(x=0, y=0, width=360, height=640)

    # Título
    Label(frame1, text="BANORTE", bg="lightgrey", font=("Arial", 24)).place(x=120, y=50)

    Label(frame1, text="Nombre(s)", bg="lightblue", font=("Arial", 14)).place(x=120, y=200)
    Entry(frame1, textvariable=nombre, font=("Arial", 14)).place(x=60, y=240, width=240)

    Label(frame1, text="Apellido(s)", bg="lightblue", font=("Arial", 14)).place(x=120, y=290)
    Entry(frame1, textvariable=apellido, font=("Arial", 14)).place(x=60, y=330, width=240)

    Button(frame1, text="Siguiente", command=lambda: mostrar_frame(frame2), font=("Arial", 14)).place(x=120, y=400, width=120)

# Pantalla 2: Correo y Teléfono
def pantalla_2():
    global frame2
    frame2 = Frame(root, bg="lightgrey")
    frame2.place(x=0, y=0, width=360, height=640)

    # Título
    Label(frame2, text="BANORTE", bg="lightgrey", font=("Arial", 24)).place(x=120, y=50)

    Label(frame2, text="Correo", bg="lightblue", font=("Arial", 14)).place(x=120, y=200)
    Entry(frame2, textvariable=correo, font=("Arial", 14)).place(x=60, y=240, width=240)

    Label(frame2, text="Teléfono", bg="lightblue", font=("Arial", 14)).place(x=120, y=290)
    Entry(frame2, textvariable=telefono, font=("Arial", 14)).place(x=60, y=330, width=240)

    Button(frame2, text="Siguiente", command=lambda: mostrar_frame(frame3), font=("Arial", 14)).place(x=120, y=400, width=120)

# Pantalla 3: Cargar archivo (INE)
def pantalla_3():
    global frame3
    frame3 = Frame(root, bg="lightgrey")
    frame3.place(x=0, y=0, width=360, height=640)

    # Título
    Label(frame3, text="BANORTE", bg="lightgrey", font=("Arial", 24)).place(x=120, y=50)

    Label(frame3, text="Carga una imagen de tu INE", bg="lightblue", font=("Arial", 14)).place(x=60, y=200)

    Button(frame3, text="Cargar imagen", command=upload_and_extract_face, font=("Arial", 14)).place(x=60, y=270, width=240)

# Función para subir el archivo y extraer el rostro
def upload_and_extract_face():
    global file_path
    file_path = filedialog.askopenfilename(
        title="Selecciona una imagen de tu INE", filetypes=[("Image files", "*.jpg *.png *.jpeg")]
    )
    if not file_path:
        return  # Si no se selecciona ninguna imagen

    try:
        # Cargar y procesar la imagen para extraer el rostro
        img = cv2.imread(file_path)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        faces = face_cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=5)
        if len(faces) > 0:
            largest_face = max(faces, key=lambda b: b[2] * b[3])
            x, y, w, h = largest_face
            face = img[y:y + h, x:x + w]

            # Guardar el rostro extraído en un archivo temporal
            face_path = os.path.join(os.getcwd(), 'face.jpg')
            cv2.imwrite(face_path, face)

            # Mostrar el rostro extraído en la ventana
            messagebox.showinfo("Éxito", "Rostro detectado y guardado. Iniciando comparación en tiempo real.")

            # Iniciar la comparación en tiempo real
            threading.Thread(target=live_match, args=(face_path,)).start()
            guardar_datos()  # Guardar datos de usuario al completar la carga

        else:
            messagebox.showwarning("Advertencia", "No se detectó ningún rostro en la imagen.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar la imagen: {e}")

# Función para el reconocimiento facial en tiempo real
def live_match(reference_img_path):
    # Cargar imagen de referencia
    reference_img = cv2.imread(reference_img_path)

    # Inicializar la cámara
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    counter = 0
    face_match = False
    match_time = 0

    def check_face(frame):
        nonlocal face_match, match_time
        try:
            # Usar DeepFace para verificar la cara en el cuadro
            if DeepFace.verify(frame, reference_img.copy())['verified']:
                face_match = True
                match_time = 0  # Reiniciar contador
            else:
                face_match = False
                match_time = 0
        except ValueError:
            face_match = False
            match_time = 0

    while True:
        ret, frame = cap.read()

        if ret:
            if counter % 38 == 8:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()

            counter += 1

            if face_match:
                cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                match_time += 1
            else:
                cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                match_time = 0

            cv2.imshow("video", frame)

            # Si el match es constante durante 4 segundos, mostrar mensaje de éxito
            if match_time > 4 * 38:  # 4 segundos en frames
                messagebox.showinfo("Éxito", "¡Verificación exitosa!")
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Configurar las pantallas
pantalla_1()
pantalla_2()
pantalla_3()

# Mostrar la pantalla inicial
mostrar_frame(frame1)

# Ejecutar la interfaz de Tkinter
root.mainloop()