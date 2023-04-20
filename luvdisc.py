import os
import pygame
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Canvas
import getpass
from mutagen.mp3 import MP3

class VinylPlayer():
    def __init__(self, root):
        self.root = root
        # Obtém o nome do usuário logado no computador
        username = getpass.getuser()
        self.root.iconbitmap("srcs/luvdisc.ico")
        # Define o título da janela
        if username == "Bianca":
            title = "I Luv(disc) you Bianca"
        else:
            title = f"Luvdisc de {username}"
        root.title(title)

        self.vinyl_frame = tk.Frame(root)
        self.vinyl_frame.pack()

        self.canvas = Canvas(self.vinyl_frame, bg="black", width=800, height=800)
        self.canvas.pack()
        
        self.background_image = Image.open("srcs/background.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(460, 460, image=self.background_photo)

        self.image = Image.open("srcs/vinyl.png")
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_frame = tk.Frame(self.vinyl_frame)
        self.image_frame.pack(side=tk.TOP, pady=15)
        self.photo_label = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="vinyl_image")
        self.image_frame.bind("<Configure>", self.on_frame_configure)
        # posiciona o frame acima dos botões e centraliza horizontalmente
        self.image_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # cria um frame para os botões
        self.buttons_frame = tk.Frame(root, highlightthickness=0)
        self.buttons_frame.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        self.prev_button = tk.Button(self.buttons_frame, text="Prev", command=self.prev_track, highlightthickness=0, bd=0)
        self.prev_button.pack(side=tk.LEFT, padx=20)

        self.play_button = tk.Button(self.buttons_frame, text="Play", command=self.play_pause, highlightthickness=0, bd=0)
        self.play_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(self.buttons_frame, text="Next", command=self.next_track, highlightthickness=0, bd=0)
        self.next_button.pack(side=tk.LEFT, padx=20)

        # adiciona uma barra de volume
        self.volume_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_scale.set(50)
        self.volume_scale.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # lista com as faixas do álbum
        self.tracks = sorted(os.listdir("aurora"))
        self.current_track_index = 0

        # configurações iniciais
        self.angle = 0
        self.is_rotating = False
        self.is_paused = True

        # inicializa o mixer do pygame
        pygame.mixer.init()

        # define o evento de fim da música
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

    def play_pause(self):
        if not pygame.get_init():   
            pygame.init()
        # inverte a direção da rotação e o estado de pausa
        self.is_rotating = not self.is_rotating
        self.is_paused = not self.is_paused

        # inicia/para a animação
        if self.is_rotating:
            self.rotate_image()
        else:
            self.root.after_cancel(self.animation)

        # toca/pausa a música
        if self.is_paused:
            pygame.mixer.music.pause()
            self.play_button.configure(text="Play")
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.play_button.configure(text="Pause")
            else:
                track_path = os.path.join("aurora", self.tracks[self.current_track_index])
                audio = MP3(track_path)
                duration = audio.info.length
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
                self.play_button.configure(text="Pause")
                self.root.after(int(duration * 1000), self.next_track)

        
    def set_volume(self, value):
        # converte o valor da barra de volume de 0-100 para 0.0-1.0
        volume = float(value) / 100.0
        pygame.mixer.music.set_volume(volume)

    def rotate_image(self):
        # rotaciona a imagem em 1 grau
        self.angle = (self.angle + 2) % 360
        rotated_image = self.image.rotate(self.angle)
        self.photo = ImageTk.PhotoImage(rotated_image)
        self.canvas.itemconfigure("vinyl_image", image=self.photo)

        # configura a próxima chamada da função após 50ms
        self.animation = self.root.after(50, self.rotate_image)

    def prev_track(self):
        # para a música atual
        pygame.mixer.music.stop()

        # seleciona a faixa anterior
        self.current_track_index -= 1
        if self.current_track_index < 0:
            self.current_track_index = len(self.tracks) - 1

        # toca a nova faixa
        track_path = os.path.join("aurora", self.tracks[self.current_track_index])
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play()

    def next_track(self):
        # para a música atual
        pygame.mixer.music.stop()

        # seleciona a próxima faixa
        self.current_track_index += 1
        if self.current_track_index >= len(self.tracks):
            self.current_track_index = 0

        # toca a nova faixa
        track_path = os.path.join("aurora", self.tracks[self.current_track_index])
        audio = MP3(track_path)
        duration = audio.info.length
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play()
        self.root.after(int(duration * 1000), self.next_track)

    def on_frame_configure(self, event):
        # ajusta a posição da imagem quando o tamanho do frame mudar
        self.canvas.coords(self.photo_label, event.width / 2, 0)

root = tk.Tk()
root.geometry("360x480")

player = VinylPlayer(root)

root.mainloop()
