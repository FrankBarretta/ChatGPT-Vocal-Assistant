#main.py

import openai
import sys
import pyttsx3
import speech_recognition as sr
import keyboard
from config import API_KEY, MODEL_NAME, TEMPERATURE, SPEAK_RESPONSE, VOICE_INPUT, LANGUAGE, HOLD_TO_SPEAK_KEYS

def speak(text):
    """Converte il testo in audio usando il motore di sintesi vocale predefinito del sistema operativo."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_and_transcribe(language):
    """Ascolta l'audio dell'utente e trascrive usando il riconoscimento vocale."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Ascoltando...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            print("Scusa, non ho capito l'audio.")
            return None
        except sr.RequestError:
            print("Errore di servizio; riprova.")
            return None

def chat_with_gpt(api_key, model_name, temperature):
    # Configura la chiave API di OpenAI
    openai.api_key = api_key

    # Presentazione iniziale
    print(f"Chatta con {model_name}! Temperatura impostata a {temperature}. Digita 'exit' per uscire.")

    while True:
        if VOICE_INPUT:
            print(f"Premi e tieni premuto {HOLD_TO_SPEAK_KEYS} per parlare o digita il tuo messaggio:")

            # Attendi che l'utente inizi a digitare o tenga premuto il tasto per l'input vocale
            started_typing = False
            while True:
                if keyboard.is_pressed(HOLD_TO_SPEAK_KEYS):  # Se l'utente tiene premuto il tasto, ascolta
                    user_message = listen_and_transcribe(LANGUAGE)
                    if user_message:
                        print(f"Tu (voce): {user_message}")  # Stampa il messaggio trascritto dell'utente
                        break  # Usciamo dal loop di attesa se abbiamo ottenuto un messaggio
                elif any(keyboard.is_pressed(key) for key in 'abcdefghijklmnopqrstuvwxyz'):  # Se l'utente inizia a digitare
                    started_typing = True
                    break

            # Se l'utente ha iniziato a digitare, prendiamo l'input da tastiera
            if started_typing:
                user_message = input("Tu: ")
        else:
            user_message = input("Tu: ")

        if user_message.lower() == 'exit':
            print("Arrivederci!")
            sys.exit(0)
        
        # Invia il messaggio all'API di OpenAI e ottieni la risposta
        response = openai.ChatCompletion.create(
          model=model_name,
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
          temperature=temperature
        )

        # Risposta di ChatGPT
        chat_response = response.choices[0].message['content']

        # Stampa e, se necessario, leggi ad alta voce la risposta
        print(f"ChatGPT: {chat_response}")
        if SPEAK_RESPONSE:
            speak(chat_response)

if __name__ == "__main__":
    # Controlla se la chiave API è stata inserita in config.py. In caso contrario, chiedi all'utente di inserirla.
    if not API_KEY:
        API_KEY = input("Inserisci la tua chiave API di OpenAI: ")

    chat_with_gpt(API_KEY, MODEL_NAME, TEMPERATURE)
