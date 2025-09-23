#!/usr/bin/env python3
"""
Jarvis Simples - Versão com reconhecimento mais básico para teste
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


class JarvisSimple:
    """Versão simples do assistente Jarvis para teste"""
    
    def __init__(self, hotword: str = "jarvis", model_path: str = None):
        self.hotword = "jarvis"  # Sempre usar jarvis
        self.is_listening = False
        self.is_processing_command = False
        
        # Configuração de áudio
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        
        # Configuração de logging
        self._setup_logging()
        
        # Inicialização dos componentes
        self._init_porcupine()
        self._init_vosk(model_path)
        self._init_command_mapping()
        
        self.logger.info("Jarvis Simples inicializado!")
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('JarvisSimple')
    
    def _init_porcupine(self):
        """Inicializa o Porcupine para detecção de hotword"""
        try:
            access_key = os.getenv('PORCUPINE_ACCESS_KEY', '')
            
            if access_key:
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=[self.hotword]
                )
                self.logger.info(f"✅ Porcupine OK - hotword: {self.hotword}")
            else:
                raise Exception("Chave do Porcupine não configurada")
        except Exception as e:
            self.logger.error(f"❌ Erro Porcupine: {e}")
            self.porcupine = None
    
    def _init_vosk(self, model_path: str = None):
        """Inicializa o Vosk para reconhecimento de voz"""
        try:
            if model_path is None:
                model_path = self._find_vosk_model()
            
            if model_path and os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
                self.logger.info(f"✅ Vosk OK - modelo: {model_path}")
            else:
                self.logger.warning("⚠️  Vosk não encontrado - usando modo teste")
                self.vosk_model = None
                self.vosk_recognizer = None
        except Exception as e:
            self.logger.error(f"❌ Erro Vosk: {e}")
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
            "arquivos": self._list_files
        }
        
        self.logger.info(f"📋 {len(self.commands)} comandos carregados")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback para captura de áudio"""
        if status:
            self.logger.warning(f"Status áudio: {status}")
        
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
                    self.logger.info(f"🔥 HOTWORD DETECTADA!")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Erro hotword: {e}")
            return False
    
    def _recognize_speech(self, audio_data: bytes) -> str:
        """Reconhece fala usando Vosk"""
        if self.vosk_recognizer is None:
            # Modo teste - retorna comando padrão
            return "teste"
        
        try:
            # Processar todo o áudio de uma vez
            if self.vosk_recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.vosk_recognizer.Result())
                text = result.get('text', '').strip().lower()
                return text
            else:
                # Tentar resultado parcial
                partial = json.loads(self.vosk_recognizer.PartialResult())
                partial_text = partial.get('partial', '').strip().lower()
                return partial_text
        except Exception as e:
            self.logger.error(f"Erro reconhecimento: {e}")
            return ""
    
    def _find_command(self, text: str) -> Optional[str]:
        """Encontra comando correspondente"""
        if not text:
            return None
        
        # Busca exata
        if text in self.commands:
            return text
        
        # Busca por palavras-chave simples
        words = text.split()
        for word in words:
            if word in self.commands:
                return word
        
        return None
    
    def _execute_command(self, command: str):
        """Executa o comando"""
        if command in self.commands:
            self.logger.info(f"🚀 EXECUTANDO: {command}")
            try:
                self.commands[command]()
                self.logger.info(f"✅ SUCESSO!")
            except Exception as e:
                self.logger.error(f"❌ ERRO: {e}")
        else:
            self.logger.warning(f"❓ COMANDO DESCONHECIDO: {command}")
    
    def _listen_for_command(self):
        """Escuta por comandos"""
        self.logger.info("🎤 ESCUTANDO COMANDO...")
        self.is_processing_command = True
        
        # Coletar áudio por 5 segundos
        command_audio = b""
        start_time = time.time()
        
        while time.time() - start_time < 5.0:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                command_audio += audio_data
            except queue.Empty:
                continue
        
        # Reconhecer
        recognized_text = self._recognize_speech(command_audio)
        
        if recognized_text:
            self.logger.info(f"🎤 RECONHECIDO: '{recognized_text}'")
            
            command = self._find_command(recognized_text)
            if command:
                self._execute_command(command)
            else:
                self.logger.info("❓ COMANDO NÃO ENCONTRADO")
                self.logger.info("💡 Comandos: teste, hora, data, ajuda, navegador, arquivos")
        else:
            self.logger.info("❌ NADA RECONHECIDO")
            self.logger.info("💡 Tente: teste, hora, data")
        
        self.is_processing_command = False
    
    def start_listening(self):
        """Inicia escuta"""
        self.logger.info("🎧 INICIANDO ESCUTA...")
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
                        self.logger.info("👋 PARANDO...")
                        break
                        
        except Exception as e:
            self.logger.error(f"Erro escuta: {e}")
        finally:
            self.stop_listening()
    
    def stop_listening(self):
        """Para escuta"""
        self.is_listening = False
        self.logger.info("🔇 PARADO")
    
    # Comandos simples
    def _test_command(self):
        """Comando de teste"""
        self.logger.info("🧪 TESTE EXECUTADO!")
    
    def _show_time(self):
        """Mostra hora"""
        result = subprocess.run(["date", "+%H:%M:%S"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"🕐 HORA: {result.stdout.strip()}")
    
    def _show_date(self):
        """Mostra data"""
        result = subprocess.run(["date"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"📅 DATA: {result.stdout.strip()}")
    
    def _open_browser(self):
        """Abre navegador"""
        subprocess.run(["xdg-open", "https://www.google.com"], check=False)
        self.logger.info("🌐 NAVEGADOR ABERTO")
    
    def _list_files(self):
        """Lista arquivos"""
        result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info("📁 ARQUIVOS:")
            print(result.stdout)
    
    def _show_help(self):
        """Mostra ajuda"""
        self.logger.info("📋 COMANDOS:")
        for cmd in sorted(self.commands.keys()):
            print(f"   - {cmd}")


def main():
    """Função principal"""
    print("🤖 Jarvis Simples - Teste")
    print("=" * 30)
    
    try:
        jarvis = JarvisSimple()
        
        print("✅ Jarvis Simples pronto!")
        print("🎤 Diga 'Jarvis' + comando")
        print("💡 Comandos: teste, hora, data, ajuda")
        print()
        
        jarvis.start_listening()
        
    except KeyboardInterrupt:
        print("\n👋 Encerrado")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
