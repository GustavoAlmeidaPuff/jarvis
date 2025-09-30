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
        
        # Configurações personalizáveis
        self.nome = "Gustavo"  # Nome para personalização
        self.cmatrix_process = None  # Processo do cmatrix
        self.cmatrix_control_file = "/tmp/jarvis_cmatrix_control"  # Arquivo de controle
        
        # Configuração de áudio
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        
        # Configuração de logging
        self._setup_logging()
        
        # Iniciar cmatrix em tela separada (após logger estar pronto)
        self._start_cmatrix()
        
        # Inicialização dos componentes
        self._init_pygame()
        self._init_tts()
        self._init_porcupine()
        self._init_vosk(model_path)
        self._init_command_mapping()
        
        # Tocar som de inicialização
        self._play_startup_sound()
        
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
        # TTS desabilitado por enquanto - descomente quando quiser usar
        self.tts_lang = None
        self.tts_slow = False
        self.logger.info("🔇 Sistema de síntese de voz desabilitado")
        
        # Código original comentado para uso futuro:
        # try:
        #     # Configurar gTTS para português brasileiro
        #     self.tts_lang = 'pt-br'  # Português brasileiro
        #     self.tts_slow = False    # Velocidade normal (mais natural)
        #     
        #     self.logger.info("✅ Sistema de síntese de voz gTTS inicializado")
        #     self.logger.info(f"🌍 Idioma configurado: {self.tts_lang}")
        # except Exception as e:
        #     self.logger.warning(f"⚠️  Erro ao inicializar gTTS: {e}")
        #     self.logger.info("💡 Respostas por voz não estarão disponíveis")
        #     self.tts_lang = None
    
    def _play_startup_sound(self):
        """Reproduz som de inicialização"""
        try:
            sound_file = os.path.join(os.getcwd(), 'ligar.mp3')
            if os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                
                # Aguardar a reprodução terminar
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                    
                self.logger.info("✅ Som de inicialização reproduzido")
            else:
                self.logger.warning(f"⚠️  Arquivo de som de inicialização não encontrado: {sound_file}")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao reproduzir som de inicialização: {e}")
    
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
    
    def _speak(self, text: str, force_speak: bool = False):
        """Fala o texto usando gTTS - apenas para comando olá"""
        if force_speak:
            # Apenas para o comando olá - ativa TTS temporariamente
            try:
                self.logger.info(f"🗣️  Falando: {text}")
                
                # Configurar gTTS temporariamente
                tts_lang = 'pt-br'
                tts_slow = False
                
                # Criar arquivo temporário para o áudio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    temp_path = tmp_file.name
                
                # Gerar áudio com gTTS
                tts = gTTS(text=text, lang=tts_lang, slow=tts_slow)
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
            # Para todos os outros comandos - apenas log
            self.logger.info(f"💬 [TTS DESABILITADO] {text}")
        
        # Código original comentado para uso futuro:
        # if self.tts_lang:
        #     try:
        #         self.logger.info(f"🗣️  Falando: {text}")
        #         
        #         # Criar arquivo temporário para o áudio
        #         with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        #             temp_path = tmp_file.name
        #         
        #         # Gerar áudio com gTTS
        #         tts = gTTS(text=text, lang=self.tts_lang, slow=self.tts_slow)
        #         tts.save(temp_path)
        #         
        #         # Reproduzir o áudio
        #         pygame.mixer.music.load(temp_path)
        #         pygame.mixer.music.play()
        #         
        #         # Aguardar a reprodução terminar
        #         while pygame.mixer.music.get_busy():
        #             pygame.time.wait(100)
        #         
        #         # Limpar arquivo temporário
        #         os.unlink(temp_path)
        #         
        #     except Exception as e:
        #         self.logger.warning(f"⚠️  Erro ao falar com gTTS: {e}")
        #         self.logger.info(f"💬 {text}")
        # else:
        #     self.logger.info(f"💬 {text}")
    
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
            "status": self._system_status,
            "olá": self._greeting_command,
            "ola": self._greeting_command,
            "trabalho": self._work_mode_command,
            "música": self._open_music,
            "musica": self._open_music,
            "biblioteca": self._open_library,
            "desliga": self._shutdown_command,
            "fechar": self._close_jarvis
        }
        
        self.logger.info(f"📋 Mapeamento de comandos inicializado com {len(self.commands)} comandos")
    
    def _start_cmatrix(self):
        """Inicia cmatrix em uma tela separada"""
        try:
            self.logger.info("🖥️  Iniciando interface tecnológica (cmatrix)...")
            
            # Verificar se cmatrix está disponível
            result = subprocess.run(["which", "cmatrix"], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.warning("⚠️  cmatrix não encontrado, continuando sem interface visual")
                return
            
            # Criar arquivo de controle
            with open(self.cmatrix_control_file, "w") as f:
                f.write("RUNNING\n")
            
            # Criar script temporário para cmatrix
            cmatrix_script = "/tmp/jarvis_cmatrix.sh"
            with open(cmatrix_script, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("CONTROL_FILE='" + self.cmatrix_control_file + "'\n")
                f.write("trap 'echo STOPPED > $CONTROL_FILE; kill $CMATRIX_PID 2>/dev/null; exit 0' SIGTERM\n")
                f.write("cmatrix -C green -s -a &\n")
                f.write("CMATRIX_PID=$!\n")
                f.write("while [ -f $CONTROL_FILE ] && [ \"$(cat $CONTROL_FILE)\" = \"RUNNING\" ]; do\n")
                f.write("    sleep 0.1\n")
                f.write("done\n")
                f.write("kill $CMATRIX_PID 2>/dev/null\n")
                f.write("rm -f $CONTROL_FILE\n")
            
            # Tornar executável
            os.chmod(cmatrix_script, 0o755)
            
            # Iniciar cmatrix em terminal separado
            cmatrix_cmd = [
                "gnome-terminal", 
                "--title=Jarvis Matrix Interface",
                "--geometry=80x24",
                "--",
                "bash", cmatrix_script
            ]
            
            # Tentar iniciar cmatrix e armazenar o processo
            self.cmatrix_process = subprocess.Popen(cmatrix_cmd, 
                                                   stdout=subprocess.DEVNULL, 
                                                   stderr=subprocess.DEVNULL)
            
            self.logger.info("✅ Interface tecnológica iniciada!")
            
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao iniciar cmatrix: {e}")
            self.logger.info("💡 Jarvis continuará funcionando normalmente")
    
    def _stop_cmatrix(self):
        """Para o cmatrix se estiver rodando"""
        try:
            if os.path.exists(self.cmatrix_control_file):
                self.logger.info("🖥️  Fechando interface tecnológica (cmatrix)...")
                
                # Sinalizar para parar via arquivo de controle
                with open(self.cmatrix_control_file, "w") as f:
                    f.write("STOPPED\n")
                
                # Aguardar um pouco para o script processar
                time.sleep(1)
                
                # Limpar arquivo de controle
                if os.path.exists(self.cmatrix_control_file):
                    os.remove(self.cmatrix_control_file)
                
                # Matar processos relacionados como fallback
                subprocess.run(["pkill", "-f", "jarvis_cmatrix.sh"], 
                             capture_output=True, timeout=1)
                subprocess.run(["pkill", "-f", "cmatrix"], 
                             capture_output=True, timeout=1)
                
                self.logger.info("✅ Interface tecnológica fechada!")
            else:
                self.logger.info("💡 Interface tecnológica já estava fechada")
                
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao fechar cmatrix: {e}")
            self.logger.info("💡 Continuando com o fechamento do Jarvis...")
    
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
        # self._speak(f"São {time_str}")  # TTS desabilitado
    
    def _show_date(self):
        """Mostra a data atual"""
        result = subprocess.run(["date"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"📅 Data atual: {result.stdout.strip()}")
    
    def _open_browser(self):
        """Abre o navegador padrão"""
        subprocess.run(["xdg-open", "https://www.google.com"], check=False)
        self.logger.info("🌐 Navegador aberto")
    
    def _system_status(self):
        """Mostra status do sistema"""
        result = subprocess.run(["uptime"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"⚡ Status do sistema: {result.stdout.strip()}")
    
    def _greeting_command(self):
        """Comando de saudação personalizado"""
        greeting = self._get_greeting()
        time_str = self._get_time_string()
        message = f"{greeting} {self.nome}, são {time_str}."
        
        self.logger.info(f"👋 {message}")
        self._speak(message, force_speak=True)  # Único comando que mantém fala ativa
    
    def _show_help(self):
        """Mostra comandos disponíveis"""
        self.logger.info("📋 Comandos disponíveis:")
        
        command_descriptions = {
            "teste": "Testa se o Jarvis está funcionando",
            "hora": "Mostra a hora atual",
            "data": "Mostra a data atual",
            "ajuda": "Lista todos os comandos disponíveis",
            "navegador": "Abre o navegador Chrome",
            "status": "Mostra status do sistema",
            "olá": "Saudação personalizada",
            "trabalho": "Abre aplicativos de trabalho",
            "música": "Abre o Spotify",
            "musica": "Abre o Spotify",
            "biblioteca": "Abre Cursor na pasta Bibliotech",
            "desliga": "Desliga o computador completamente",
            "fechar": "Encerra o Jarvis"
        }
        
        for command in sorted(self.commands.keys()):
            description = command_descriptions.get(command, "Comando disponível")
            print(f"   - {command}: {description}")
    
    def _work_mode_command(self):
        """Abre todos os aplicativos de trabalho"""
        self.logger.info("💼 Iniciando modo de trabalho...")
        
        # Tocar som de trabalho
        try:
            self.logger.info("🔊 Reproduzindo som de trabalho...")
            pygame.mixer.music.load("muhehe.mp3")
            pygame.mixer.music.play()
            
            # Aguardar a reprodução terminar
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
            self.logger.info("✅ Som de trabalho reproduzido")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao reproduzir som de trabalho: {e}")
        
        # Lista de aplicativos para abrir
        apps = [
            ("Slack", ["slack"]),
            ("Spotify", ["spotify"]),
            ("Cursor", ["cursor"]),
            ("Navegador", ["google-chrome"])
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
        
        # Resposta por voz desabilitada
        if opened_apps:
            self.logger.info("💼 Aplicativos de trabalho abertos!")
        else:
            self.logger.error("❌ Nenhum aplicativo foi aberto")
            self.logger.info("💡 Desculpe, não consegui abrir os aplicativos de trabalho.")
    
    def _open_library(self):
        """Abre Cursor na pasta Bibliotech"""
        try:
            library_path = os.path.expanduser("~/code/Bibliotech")
            self.logger.info(f"📁 Caminho da biblioteca: {library_path}")
            
            # Verificar se a pasta existe
            if not os.path.exists(library_path):
                self.logger.warning(f"⚠️  Pasta não encontrada: {library_path}")
                self.logger.info("💡 Criando pasta Bibliotech...")
                os.makedirs(library_path, exist_ok=True)
                self.logger.info("✅ Pasta Bibliotech criada!")
            else:
                self.logger.info("✅ Pasta Bibliotech já existe")
            
            # Abrir Cursor na pasta usando diferentes métodos
            self.logger.info(f"📚 Abrindo Cursor na pasta Bibliotech...")
            
            # Método 1: Usar os.system (mais robusto com interferência de áudio)
            self.logger.info("🔄 Tentativa 1: Usando os.system...")
            try:
                cmd = f"cd '{library_path}' && cursor . &"
                result = os.system(cmd)
                if result == 0:
                    self.logger.info("✅ Cursor aberto com os.system!")
                    time.sleep(1)
                    # Tentar focar a janela
                    os.system("wmctrl -a 'Bibliotech' 2>/dev/null || true")
                    self.logger.info("🎉 Biblioteca aberta com sucesso!")
                    return
                else:
                    self.logger.warning(f"⚠️  os.system retornou código: {result}")
            except Exception as e:
                self.logger.warning(f"⚠️  Erro com os.system: {e}")
            
            # Método 2: Script temporário
            self.logger.info("🔄 Tentativa 2: Usando script temporário...")
            script_path = "/tmp/jarvis_open_cursor.sh"
            try:
                with open(script_path, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write(f"cd '{library_path}'\n")
                    f.write("cursor . &\n")
                    f.write("sleep 1\n")
                    f.write("wmctrl -a 'Bibliotech' 2>/dev/null || true\n")
                
                # Tornar executável
                os.chmod(script_path, 0o755)
                
                # Executar o script
                result = subprocess.run([script_path], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=10)
                
                if result.returncode == 0:
                    self.logger.info("✅ Script executado com sucesso!")
                    self.logger.info("🎉 Biblioteca aberta com sucesso!")
                    return
                else:
                    self.logger.warning(f"⚠️  Script retornou código: {result.returncode}")
                    if result.stderr:
                        self.logger.warning(f"Erro: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️  Script demorou muito para executar")
            except Exception as e:
                self.logger.warning(f"⚠️  Erro ao executar script: {e}")
            
            # Método 3: Fallback com subprocess.Popen
            self.logger.info("🔄 Tentativa 3: Usando subprocess.Popen...")
            try:
                process = subprocess.Popen(["cursor", library_path], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                time.sleep(2)
                
                if process.poll() is None:
                    self.logger.info("✅ Cursor aberto via subprocess!")
                    self.logger.info("🎉 Biblioteca aberta com sucesso!")
                else:
                    self.logger.error("❌ Todos os métodos falharam")
                    self.logger.info("💡 Tente executar manualmente: cursor ~/code/Bibliotech")
                    
            except Exception as e:
                self.logger.error(f"❌ Erro no subprocess: {e}")
                self.logger.info("💡 Tente executar manualmente: cursor ~/code/Bibliotech")
            
            # Limpar script temporário
            try:
                os.remove(script_path)
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado: {e}")
            self.logger.info("💡 Não foi possível abrir a biblioteca")
    
    def _open_music(self):
        """Abre o Spotify para música"""
        try:
            self.logger.info("🎵 Abrindo Spotify...")
            
            # Método 1: Usar os.system (mais robusto)
            self.logger.info("🔄 Tentativa 1: Usando os.system...")
            try:
                cmd = "spotify &"
                result = os.system(cmd)
                if result == 0:
                    self.logger.info("✅ Spotify aberto com os.system!")
                    time.sleep(1)
                    # Tentar focar a janela do Spotify
                    os.system("wmctrl -a 'Spotify' 2>/dev/null || true")
                    self.logger.info("🎉 Spotify aberto com sucesso!")
                    return
                else:
                    self.logger.warning(f"⚠️  os.system retornou código: {result}")
            except Exception as e:
                self.logger.warning(f"⚠️  Erro com os.system: {e}")
            
            # Método 2: Fallback com subprocess.Popen
            self.logger.info("🔄 Tentativa 2: Usando subprocess.Popen...")
            try:
                process = subprocess.Popen(["spotify"], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                time.sleep(2)
                
                if process.poll() is None:
                    self.logger.info("✅ Spotify aberto via subprocess!")
                    self.logger.info("🎉 Spotify aberto com sucesso!")
                else:
                    self.logger.error("❌ Não foi possível abrir o Spotify")
                    self.logger.info("💡 Verifique se o Spotify está instalado")
                    self.logger.info("💡 Tente executar manualmente: spotify")
                    
            except Exception as e:
                self.logger.error(f"❌ Erro no subprocess: {e}")
                self.logger.info("💡 Tente executar manualmente: spotify")
            
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado: {e}")
            self.logger.info("💡 Não foi possível abrir o Spotify")
    
    def _shutdown_command(self):
        """Desliga o computador completamente"""
        self.logger.info("🔌 Comando de desligamento recebido...")
        
        # Confirmação por voz desabilitada
        self.logger.info("🔌 Desligando o computador em 5 segundos...")
        
        # Aguarda 5 segundos
        for i in range(5, 0, -1):
            self.logger.info(f"⏰ Desligando em {i} segundos...")
            time.sleep(1)
        
        try:
            # Comando para desligar o sistema
            self.logger.info("🔌 Executando comando de desligamento...")
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Erro ao desligar: {e}")
            self.logger.info("💡 Desculpe, não consegui desligar o computador. Verifique as permissões.")
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado: {e}")
            self.logger.info("💡 Ocorreu um erro ao tentar desligar o computador.")
    
    def _close_jarvis(self):
        """Fecha o Jarvis com som de despedida"""
        self.logger.info("👋 Comando de fechamento recebido...")
        
        # Fechar cmatrix se estiver rodando
        self._stop_cmatrix()
        
        # Tocar som de fechamento
        try:
            self.logger.info("🔊 Reproduzindo som de despedida...")
            pygame.mixer.music.load("fechar.mp3")
            pygame.mixer.music.play()
            
            # Aguardar a reprodução terminar
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
            self.logger.info("✅ Som de despedida reproduzido")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao reproduzir som de fechamento: {e}")
        
        # Parar a escuta
        self.logger.info("🔌 Encerrando Jarvis...")
        self.is_listening = False
        
        # Log de despedida
        self.logger.info("✅ Jarvis encerrado com sucesso!")
        print("\n👋 Jarvis encerrado. Até logo!")
        
        # Encerrar o programa
        exit(0)


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
