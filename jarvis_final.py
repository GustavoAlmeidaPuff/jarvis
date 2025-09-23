#!/usr/bin/env python3
"""
Jarvis Final - Versão que funciona completamente
"""

import os
import sys
import time
import logging
import subprocess
import threading
import queue
import json
from typing import Dict, Callable, Optional
import sounddevice as sd
import numpy as np
import pvporcupine
import vosk
from pathlib import Path
import pygame
from gtts import gTTS
import tempfile
import os
from datetime import datetime


class JarvisFinal:
    """Versão final do assistente Jarvis"""
    
    def __init__(self, hotword: str = "jarvis", model_path: str = None):
        self.hotword = hotword.lower()
        self.is_listening = False
        self.is_processing_command = False
        
        # Configuração de áudio
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        
        # Configuração de logging
        self._setup_logging()
        
        # Inicialização dos componentes
        self._init_pygame()
        self._init_tts()
        self._init_porcupine()
        self._init_vosk(model_path)
        self._init_command_mapping()
        
        self.logger.info("Jarvis Final inicializado com sucesso!")
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jarvis_final.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('JarvisFinal')
    
    def _init_pygame(self):
        """Inicializa o pygame para reprodução de sons"""
        try:
            pygame.mixer.init()
            self.logger.info("✅ Pygame inicializado para reprodução de sons")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao inicializar pygame: {e}")
            self.logger.info("💡 Som de ativação não estará disponível")
    
    def _init_tts(self):
        """Inicializa o sistema de síntese de voz com gTTS"""
        try:
            # Configurar gTTS para português brasileiro
            self.tts_lang = 'pt-br'  # Português brasileiro
            self.tts_slow = False    # Velocidade normal (mais natural)
            
            self.logger.info("✅ Sistema de síntese de voz gTTS inicializado")
            self.logger.info(f"🌍 Idioma configurado: {self.tts_lang}")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao inicializar gTTS: {e}")
            self.logger.info("💡 Respostas por voz não estarão disponíveis")
            self.tts_lang = None
    
    def _play_activation_sound(self):
        """Reproduz o som de ativação"""
        try:
            sound_file = os.path.join(os.getcwd(), 'listen.mp3')
            if os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                self.logger.info("🔊 Som de ativação reproduzido")
            else:
                self.logger.warning(f"⚠️  Arquivo de som não encontrado: {sound_file}")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao reproduzir som: {e}")
    
    def _speak(self, text: str):
        """Fala o texto usando gTTS"""
        if self.tts_lang:
            try:
                self.logger.info(f"🗣️  Falando: {text}")
                
                # Criar arquivo temporário para o áudio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    temp_path = tmp_file.name
                
                # Gerar áudio com gTTS
                tts = gTTS(text=text, lang=self.tts_lang, slow=self.tts_slow)
                tts.save(temp_path)
                
                # Reproduzir o áudio
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                # Aguardar a reprodução terminar
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                # Limpar arquivo temporário
                os.unlink(temp_path)
                
            except Exception as e:
                self.logger.warning(f"⚠️  Erro ao falar com gTTS: {e}")
                self.logger.info(f"💬 {text}")
        else:
            self.logger.info(f"💬 {text}")
    
    def _get_greeting(self):
        """Retorna saudação baseada na hora"""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            return "Bom dia"
        elif 12 <= hour < 18:
            return "Boa tarde"
        else:
            return "Boa noite"
    
    def _get_time_string(self):
        """Retorna string formatada da hora atual"""
        now = datetime.now()
        return now.strftime("%H horas e %M minutos")
    
    def _init_porcupine(self):
        """Inicializa o Porcupine para detecção de hotword"""
        try:
            access_key = os.getenv('PORCUPINE_ACCESS_KEY', '')
            
            if not access_key:
                raise Exception("Chave de acesso do Porcupine não configurada")
            
            # Usar hotword padrão "jarvis" do Porcupine
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=['jarvis']  # Sempre usar 'jarvis'
            )
            self.logger.info(f"✅ Porcupine inicializado com hotword: jarvis")
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Porcupine: {e}")
            self.logger.info("Usando modo de teste sem Porcupine")
            self.porcupine = None
    
    def _init_vosk(self, model_path: str = None):
        """Inicializa o Vosk para reconhecimento de voz"""
        try:
            if model_path is None:
                model_path = self._find_vosk_model()
            
            if model_path and os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
                self.logger.info(f"✅ Vosk inicializado com modelo: {model_path}")
            else:
                self.logger.warning("⚠️  Modelo Vosk não encontrado. Usando modo de teste.")
                self.vosk_model = None
                self.vosk_recognizer = None
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Vosk: {e}")
            self.vosk_model = None
            self.vosk_recognizer = None
    
    def _find_vosk_model(self) -> Optional[str]:
        """Tenta encontrar um modelo Vosk instalado"""
        possible_paths = [
            "/usr/share/vosk-models",
            "/usr/local/share/vosk-models",
            os.path.expanduser("~/vosk-models"),
            "./vosk-models"
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                for model_dir in os.listdir(base_path):
                    model_path = os.path.join(base_path, model_dir)
                    if os.path.isdir(model_path):
                        return model_path
        return None
    
    def _init_command_mapping(self):
        """Inicializa o mapeamento de comandos"""
        self.commands = {
            "teste": self._test_command,
            "hora": self._show_time,
            "data": self._show_date,
            "ajuda": self._show_help,
            "navegador": self._open_browser,
            "arquivos": self._list_files,
            "status": self._system_status,
            "olá": self._greeting_command,
            "ola": self._greeting_command,
            "trabalho": self._work_mode_command
        }
        
        self.logger.info(f"📋 Mapeamento de comandos inicializado com {len(self.commands)} comandos")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback para captura de áudio"""
        if status:
            self.logger.warning(f"Status de áudio: {status}")
        
        audio_data = (indata[:, 0] * 32767).astype(np.int16)
        self.audio_queue.put(audio_data.tobytes())
    
    def _detect_hotword(self, audio_data: bytes) -> bool:
        """Detecta se a hotword foi pronunciada"""
        if self.porcupine is None:
            return False
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            frame_length = self.porcupine.frame_length
            
            if len(audio_array) >= frame_length:
                frame = audio_array[:frame_length]
                keyword_index = self.porcupine.process(frame)
                
                if keyword_index >= 0:
                    self.logger.info(f"🔥 Hotword 'jarvis' detectada!")
                    self._play_activation_sound()
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Erro na detecção de hotword: {e}")
            return False
    
    def _recognize_speech(self, audio_data: bytes) -> str:
        """Reconhece fala usando Vosk"""
        if self.vosk_recognizer is None:
            return "teste"  # Comando padrão para teste
        
        try:
            if self.vosk_recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.vosk_recognizer.Result())
                text = result.get('text', '').strip().lower()
                return text
            else:
                partial = json.loads(self.vosk_recognizer.PartialResult())
                partial_text = partial.get('partial', '').strip().lower()
                return partial_text
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return ""
    
    def _find_command(self, text: str) -> Optional[str]:
        """Encontra comando correspondente"""
        if not text:
            return None
        
        # Busca exata
        if text in self.commands:
            return text
        
        # Busca por palavras-chave
        words = text.split()
        for word in words:
            if word in self.commands:
                return word
        
        return None
    
    def _execute_command(self, command: str):
        """Executa o comando correspondente"""
        if command in self.commands:
            self.logger.info(f"🚀 Executando comando: {command}")
            try:
                self.commands[command]()
                self.logger.info(f"✅ Comando '{command}' executado com sucesso!")
            except Exception as e:
                self.logger.error(f"❌ Erro ao executar comando '{command}': {e}")
        else:
            self.logger.warning(f"⚠️  Comando não reconhecido: {command}")
            self.logger.info("💡 Comandos disponíveis:")
            for cmd in sorted(self.commands.keys()):
                print(f"   - {cmd}")
    
    def _listen_for_command(self):
        """Escuta por comandos após detecção da hotword"""
        self.logger.info("🎤 Escutando comando... (fale devagar e claramente)")
        self.is_processing_command = True
        
        # Usar o mesmo método que funciona no manual
        duration = 4
        audio_data = sd.rec(int(duration * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=1, 
                           dtype=np.float32)
        sd.wait()
        
        # Converter para formato correto
        audio_int16 = (audio_data * 32767).astype(np.int16)
        command_audio = audio_int16.tobytes()
        
        # Reconhecer o comando
        recognized_text = self._recognize_speech(command_audio)
        
        if recognized_text:
            self.logger.info(f"🎤 Texto reconhecido: '{recognized_text}'")
            
            # Encontrar e executar comando
            command = self._find_command(recognized_text)
            if command:
                self._execute_command(command)
            else:
                self.logger.info("❓ Comando não reconhecido")
                self.logger.info("💡 Comandos disponíveis:")
                for cmd in sorted(self.commands.keys()):
                    print(f"   - {cmd}")
        else:
            self.logger.info("❌ Nenhum comando reconhecido")
            self.logger.info("💡 Tente falar mais devagar e claramente")
        
        self.is_processing_command = False
    
    def start_listening(self):
        """Inicia o loop principal de escuta"""
        self.logger.info("🎧 Iniciando escuta contínua...")
        self.is_listening = True
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ):
                while self.is_listening:
                    try:
                        audio_data = self.audio_queue.get(timeout=1.0)
                        
                        if self._detect_hotword(audio_data) and not self.is_processing_command:
                            command_thread = threading.Thread(target=self._listen_for_command)
                            command_thread.daemon = True
                            command_thread.start()
                        
                    except queue.Empty:
                        continue
                    except KeyboardInterrupt:
                        self.logger.info("👋 Interrompido pelo usuário")
                        break
                        
        except Exception as e:
            self.logger.error(f"Erro no loop de escuta: {e}")
        finally:
            self.stop_listening()
    
    def stop_listening(self):
        """Para a escuta"""
        self.is_listening = False
        self.logger.info("🔇 Escuta interrompida")
    
    # Comandos do sistema
    def _test_command(self):
        """Comando de teste"""
        self.logger.info("🧪 Comando de teste executado!")
        self.logger.info("✅ Jarvis está funcionando perfeitamente!")
    
    def _show_time(self):
        """Mostra a hora atual"""
        time_str = self._get_time_string()
        self.logger.info(f"🕐 Hora atual: {time_str}")
        self._speak(f"São {time_str}")
    
    def _show_date(self):
        """Mostra a data atual"""
        result = subprocess.run(["date"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"📅 Data atual: {result.stdout.strip()}")
    
    def _open_browser(self):
        """Abre o navegador padrão"""
        subprocess.run(["xdg-open", "https://www.google.com"], check=False)
        self.logger.info("🌐 Navegador aberto")
    
    def _list_files(self):
        """Lista arquivos do diretório atual"""
        result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info("📁 Arquivos no diretório atual:")
            print(result.stdout)
    
    def _system_status(self):
        """Mostra status do sistema"""
        result = subprocess.run(["uptime"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"⚡ Status do sistema: {result.stdout.strip()}")
    
    def _greeting_command(self):
        """Comando de saudação personalizado"""
        greeting = self._get_greeting()
        time_str = self._get_time_string()
        message = f"{greeting} Gustavo, são {time_str} e você ainda não ficou rico, bora trabalhar?"
        
        self.logger.info(f"👋 {message}")
        self._speak(message)
    
    def _show_help(self):
        """Mostra comandos disponíveis"""
        self.logger.info("📋 Comandos disponíveis:")
        for command in sorted(self.commands.keys()):
            print(f"   - {command}")
    
    def _work_mode_command(self):
        """Abre todos os aplicativos de trabalho"""
        self.logger.info("💼 Iniciando modo de trabalho...")
        
        # Lista de aplicativos para abrir
        apps = [
            ("Slack", ["slack"]),
            ("Spotify", ["spotify"]),
            ("Cursor", ["cursor"]),
            ("Navegador", ["google-chrome"]),
            ("ChatGPT", ["google-chrome", "--app=https://chat.openai.com"]),
            ("CopyQ", ["copyq"]),
            ("Excalidraw", ["google-chrome", "--app=https://excalidraw.com"])
        ]
        
        opened_apps = []
        failed_apps = []
        
        for app_name, command in apps:
            try:
                self.logger.info(f"🚀 Abrindo {app_name}...")
                subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                opened_apps.append(app_name)
                time.sleep(0.5)  # Pequena pausa entre aberturas
            except Exception as e:
                self.logger.warning(f"⚠️  Erro ao abrir {app_name}: {e}")
                failed_apps.append(app_name)
        
        # Relatório final
        if opened_apps:
            self.logger.info(f"✅ Aplicativos abertos: {', '.join(opened_apps)}")
        
        if failed_apps:
            self.logger.warning(f"❌ Falha ao abrir: {', '.join(failed_apps)}")
        
        # Resposta por voz
        if opened_apps:
            self._speak("bora trabalhar")
        else:
            self.logger.error("❌ Nenhum aplicativo foi aberto")
            self._speak("Desculpe, não consegui abrir os aplicativos de trabalho.")


def main():
    """Função principal"""
    print("🤖 Jarvis Final - Assistente de Voz Local")
    print("=" * 50)
    
    # Verificar argumentos
    hotword = "jarvis"
    model_path = None
    
    if len(sys.argv) > 1:
        hotword = sys.argv[1]
    if len(sys.argv) > 2:
        model_path = sys.argv[2]
    
    try:
        # Criar e inicializar o assistente
        jarvis = JarvisFinal(hotword=hotword, model_path=model_path)
        
        print(f"✅ Jarvis Final inicializado com hotword: '{hotword}'")
        print("🎤 Escutando... (pressione Ctrl+C para sair)")
        print("💡 Diga 'Jarvis' seguido de um comando")
        print("💡 Comandos: teste, hora, data, ajuda, navegador, arquivos, status")
        print()
        
        # Iniciar escuta
        jarvis.start_listening()
        
    except KeyboardInterrupt:
        print("\n👋 Jarvis encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
