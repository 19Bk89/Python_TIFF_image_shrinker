# =======================================================
# Autor: Bernd Krammer
# Beschreibung:
# Dieses Programm ist ein einfacher TIFF-Bildmanager,
# der es dem Benutzer ermöglicht, TIFF-Bilder zu laden,
# deren Skalierungsfaktor zu berechnen und das Bild basierend
# auf diesem Faktor zu skalieren. Es zeigt die Originalgröße
# und Dateigröße sowie die skalierte Größe und Dateigröße an.
# Der Benutzer kann das skalierte Bild speichern, indem er einen
# Zielpfad auswählt.
# 
# Funktionen:
# - Bild auswählen und laden
# - Berechnung der neuen Bildgröße basierend auf einem
#   Skalierungsfaktor
# - Anzeige der Original- und skalierten Bildgrößen sowie
#   der entsprechenden Dateigrößen
# - Speichern des skalierten Bildes an einem benutzerdefinierten
#   Speicherort
#
# Voraussetzungen:
# - Python 3.x
# - Tkinter (für GUI)
# - Pillow (für Bildbearbeitung)
# =======================================================

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import io
import threading

# Globale Variablen für Bildreferenzen
displayed_image = None
original_image = None

def get_file_size_in_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def browse_file():
    global displayed_image, original_image
    file_path = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tiff;*.tif")])
    if not file_path:
        return

    entry_input.delete(0, tk.END)
    entry_input.insert(0, file_path)

    try:
        original_image = Image.open(file_path)
        display_image = original_image.copy()
        display_image.thumbnail((800, 600))  # Anzeigegröße beschränkt
        displayed_image = ImageTk.PhotoImage(display_image)
        image_label.config(image=displayed_image)

        # Originalbild-Pixelgröße anzeigen
        width, height = original_image.size
        label_size_before_info.config(text=f"{width} x {height} px")
        label_file_size_before_info.config(text=f"{get_file_size_in_mb(file_path):.2f} MB")
        
        # Skalierte Dateigröße zurücksetzen
        label_size_after_info.config(text="0.00 MB")
        label_file_size_after_info.config(text="0.00 MB")
    except Exception as e:
        messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

def update_scaled_size_thread():
    """Berechnet und zeigt die neue Bildgröße und Dateigröße basierend auf dem Skalierungsfaktor an"""
    if not original_image:
        return

    try:
        scale_factor = float(entry_scale.get())
        if scale_factor <= 0:
            raise ValueError

        # Berechnungen durchführen
        width, height = original_image.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Berechnung der neuen Bildgröße
        label_size_after_info.config(text=f"{new_width} x {new_height} px")

        # Berechnung der Dateigröße (auf Grundlage des neuen Bildes, aber ohne es zu speichern)
        img_resized = original_image.resize((new_width, new_height), Image.LANCZOS)

        # Speicher das Bild in einem BytesIO-Puffer
        with io.BytesIO() as img_byte_arr:
            img_resized.save(img_byte_arr, format='TIFF')
            size_mb = len(img_byte_arr.getvalue()) / (1024 * 1024)

        # Update der Dateigröße
        root.after(0, lambda: label_file_size_after_info.config(text=f"{size_mb:.2f} MB"))
    
    except ValueError:
        root.after(0, lambda: label_size_after_info.config(text="Ungültiger Skalierungsfaktor"))
        root.after(0, lambda: label_file_size_after_info.config(text="Ungültig"))
    
    finally:
        # Cursor zurücksetzen
        root.after(0, lambda: root.config(cursor=""))

def update_scaled_size(event=None):
    """Funktion zum Starten des Threads für die Berechnung"""
    root.config(cursor="wait")  # Setze die Maus auf "Warten"
    threading.Thread(target=update_scaled_size_thread, daemon=True).start()

def save_image():
    """Speichert das skalierte Bild an einem benutzerdefinierten Speicherort"""
    if not original_image:
        messagebox.showerror("Fehler", "Kein Bild zum Speichern vorhanden.")
        return

    try:
        scale_factor = float(entry_scale.get())
        if scale_factor <= 0:
            raise ValueError

        # Berechnen der neuen Bildgröße
        width, height = original_image.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Skalieren des Bildes
        img_resized = original_image.resize((new_width, new_height), Image.LANCZOS)

        # Speicher das Bild in einem BytesIO-Puffer
        with io.BytesIO() as img_byte_arr:
            img_resized.save(img_byte_arr, format='TIFF')

            # Öffne ein "Speichern unter"-Dialog für den Speicherort
            output_path = filedialog.asksaveasfilename(
                defaultextension=".tiff",
                filetypes=[("TIFF files", "*.tiff;*.tif")],
                title="Skaliertes Bild speichern"
            )
            if output_path:
                # Speichern des Bildes auf dem ausgewählten Pfad
                with open(output_path, "wb") as f:
                    f.write(img_byte_arr.getvalue())  # Schreibe das Bild aus dem Puffer

                messagebox.showinfo("Erfolg", f"Bild erfolgreich gespeichert unter: {output_path}")

    except ValueError:
        messagebox.showerror("Fehler", "Ungültiger Skalierungsfaktor")

# ==== GUI SETUP ==== 
root = tk.Tk()
root.title("TIFF Bildmanager")
root.configure(bg='#f0f0f0')

# === STYLES === 
style = {'font': ('Helvetica', 10), 'bg': '#f0f0f0', 'padx': 10, 'pady': 10}
button_style = {'font': ('Helvetica', 10, 'bold'), 'bg': '#4CAF50', 'fg': 'white', 'activebackground': '#45a049'}
blue_button_style = button_style.copy()
blue_button_style['bg'] = '#2196F3'

# === LAYOUT ===
main_frame = tk.Frame(root, bg=style['bg'])
main_frame.pack(padx=20, pady=20)

# Dateiauswahl
file_frame = tk.Frame(main_frame, bg=style['bg'])
file_frame.grid(row=0, column=0, columnspan=2, sticky='ew')

tk.Label(file_frame, text="TIFF-Datei:", **style).grid(row=0, column=0)
entry_input = tk.Entry(file_frame, width=40, font=style['font'])
entry_input.grid(row=0, column=1, padx=10)
tk.Button(file_frame, text="Durchsuchen", command=browse_file, **button_style).grid(row=0, column=2)

# Skalierung
scale_frame = tk.Frame(main_frame, bg=style['bg'])
scale_frame.grid(row=1, column=0, sticky='w', pady=10)
tk.Label(scale_frame, text="Skalierungsfaktor:", **style).grid(row=0, column=0)
entry_scale = tk.Entry(scale_frame, width=10, font=style['font'])
entry_scale.grid(row=0, column=1, padx=10)
entry_scale.insert(0, "1.0")

# Dateigrößenanzeige
size_frame = tk.Frame(main_frame, bg=style['bg'])
size_frame.grid(row=1, column=1, sticky='e', pady=10)

tk.Label(size_frame, text="Originalgröße:", **style).grid(row=0, column=0)
label_size_before_info = tk.Label(size_frame, text="0.00 MB", **style)
label_size_before_info.grid(row=0, column=1, padx=10)

tk.Label(size_frame, text="Original Dateigröße:", **style).grid(row=1, column=0)
label_file_size_before_info = tk.Label(size_frame, text="0.00 MB", **style)
label_file_size_before_info.grid(row=1, column=1, padx=10)

tk.Label(size_frame, text="Skalierte Größe:", **style).grid(row=2, column=0)
label_size_after_info = tk.Label(size_frame, text="0.00 MB", **style)
label_size_after_info.grid(row=2, column=1, padx=10)

tk.Label(size_frame, text="Skalierte Dateigröße:", **style).grid(row=3, column=0)
label_file_size_after_info = tk.Label(size_frame, text="0.00 MB", **style)
label_file_size_after_info.grid(row=3, column=1, padx=10)

# Button für Skalieren
button_frame = tk.Frame(main_frame, bg=style['bg'])
button_frame.grid(row=2, column=0, columnspan=2, pady=20)

tk.Button(button_frame, text="Skaliertes Bild speichern", command=lambda: save_image(), **blue_button_style).pack(side=tk.LEFT, padx=10)

# Bildanzeige
image_label = tk.Label(root, bg='white', bd=2, relief=tk.SUNKEN)
image_label.pack(padx=20, pady=10)

# Bind des Skalierungsfaktors an das Eingabefeld
entry_scale.bind("<KeyRelease>", update_scaled_size)

# Start
root.mainloop()
