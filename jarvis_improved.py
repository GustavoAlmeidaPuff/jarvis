#!/usr/bin/env python3
"""
Jarvis Melhorado - Com melhor feedback visual e reconhecimento
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


class JarvisImproved:
    """Versão melhorada do assistente Jarvis com melhor feedback"""
    
    def __init__(self, hotword: str = "jarvis", model_path: str = None):
        """
        Inicializa o assistente melhorado
        
        Args:
            hotword: Palavra de ativação (padrão: "jarvis")
            model_path: Caminho para o modelo Vosk (opcional)
        """
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
        self._init_porcupine()
        self._init_vosk(model_path)
        self._init_command_mapping()
        
        self.logger.info("Jarvis Melhorado inicializado com sucesso!")
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jarvis_improved.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('JarvisImproved')
    
    def _init_porcupine(self):
        """Inicializa o Porcupine para detecção de hotword"""
        try:
            access_key = os.getenv('PORCUPINE_ACCESS_KEY', '')
            
            if access_key:
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=[self.hotword]
                )
                self.logger.info(f"✅ Porcupine inicializado com hotword: {self.hotword}")
            else:
                raise Exception("Chave de acesso do Porcupine não configurada")
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
            "abrir navegador": self._open_browser,
            "abrir firefox": self._open_firefox,
            "abrir chrome": self._open_chrome,
            "mostrar hora": self._show_time,
            "mostrar data": self._show_date,
            "abrir vscode": self._open_vscode,
            "abrir code": self._open_vscode,
            "abrir terminal": self._open_terminal,
            "desligar computador": self._shutdown_computer,
            "reiniciar computador": self._restart_computer,
            "fechar aplicativo": self._close_application,
            "listar arquivos": self._list_files,
            "status sistema": self._system_status,
            "ajuda": self._show_help,
            "teste": self._test_command
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
                    self.logger.info(f"🔥 Hotword '{self.hotword}' detectada!")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Erro na detecção de hotword: {e}")
            return False
    
    def _recognize_speech(self, audio_data: bytes) -> str:
        """Reconhece fala usando Vosk com melhor feedback"""
        if self.vosk_recognizer is None:
            return "teste"  # Comando padrão para teste
        
        try:
            # Processar em chunks menores para melhor reconhecimento
            chunk_size = 4000  # Menor que o padrão
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                if self.vosk_recognizer.AcceptWaveform(chunk):
                    result = json.loads(self.vosk_recognizer.Result())
                    text = result.get('text', '').strip().lower()
                    if text:
                        return text
                else:
                    partial = json.loads(self.vosk_recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip().lower()
                    if partial_text:
                        self.logger.info(f"🎤 Reconhecendo: '{partial_text}'")
            
            return ""
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return ""
    
    def _find_best_command_match(self, recognized_text: str) -> Optional[str]:
        """Encontra o melhor comando correspondente ao texto reconhecido"""
        if not recognized_text:
            return None
        
        # Busca exata primeiro
        if recognized_text in self.commands:
            return recognized_text
        
        # Busca por palavras-chave com threshold mais baixo
        recognized_words = set(recognized_text.split())
        
        best_match = None
        best_score = 0
        
        for command in self.commands.keys():
            command_words = set(command.split())
            
            # Calcula similaridade
            common_words = recognized_words.intersection(command_words)
            score = len(common_words) / len(command_words)
            
            # Threshold mais baixo para melhor reconhecimento
            if score > best_score and score >= 0.3:  # 30% de similaridade
                best_match = command
                best_score = score
        
        return best_match
    
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
            self.logger.info("💡 Diga 'ajuda' para ver comandos disponíveis")
    
    def _listen_for_command(self):
        """Escuta por comandos após detecção da hotword"""
        self.logger.info("🎤 Escutando comando... (fale devagar e claramente)")
        self.is_processing_command = True
        
        # Coletar áudio por 4 segundos (mais tempo)
        command_audio = b""
        start_time = time.time()
        
        while time.time() - start_time < 4.0:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                command_audio += audio_data
            except queue.Empty:
                continue
        
        # Reconhecer o comando
        recognized_text = self._recognize_speech(command_audio)
        
        if recognized_text:
            self.logger.info(f"🎤 Texto reconhecido: '{recognized_text}'")
            
            # Encontrar e executar comando
            command = self._find_best_command_match(recognized_text)
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
    def _open_browser(self):
        """Abre o navegador padrão"""
        subprocess.run(["xdg-open", "https://www.google.com"], check=False)
    
    def _open_firefox(self):
        """Abre o Firefox"""
        subprocess.run(["firefox"], check=False)
    
    def _open_chrome(self):
        """Abre o Chrome"""
        subprocess.run(["google-chrome"], check=False)
    
    def _show_time(self):
        """Mostra a hora atual"""
        result = subprocess.run(["date", "+%H:%M:%S"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"🕐 Hora atual: {result.stdout.strip()}")
    
    def _show_date(self):
        """Mostra a data atual"""
        result = subprocess.run(["date"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"📅 Data atual: {result.stdout.strip()}")
    
    def _open_vscode(self):
        """Abre o VSCode"""
        subprocess.run(["code"], check=False)
    
    def _open_terminal(self):
        """Abre um terminal"""
        subprocess.run(["gnome-terminal"], check=False)
    
    def _shutdown_computer(self):
        """Desliga o computador"""
        self.logger.warning("⚠️  Desligando computador em 10 segundos...")
        subprocess.run(["shutdown", "-h", "+1"], check=False)
    
    def _restart_computer(self):
        """Reinicia o computador"""
        self.logger.warning("⚠️  Reiniciando computador em 10 segundos...")
        subprocess.run(["shutdown", "-r", "+1"], check=False)
    
    def _close_application(self):
        """Fecha aplicação ativa"""
        subprocess.run(["xdotool", "key", "Alt+F4"], check=False)
    
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
    
    def _test_command(self):
        """Comando de teste"""
        self.logger.info("🧪 Comando de teste executado com sucesso!")
        self.logger.info("✅ Jarvis está funcionando perfeitamente!")
    
    def _show_help(self):
        """Mostra comandos disponíveis"""
        self.logger.info("📋 Comandos disponíveis:")
        for command in sorted(self.commands.keys()):
            print(f"   - {command}")


def main():
    """Função principal"""
    print("🤖 Jarvis Melhorado - Assistente de Voz Local")
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
        jarvis = JarvisImproved(hotword=hotword, model_path=model_path)
        
        print(f"✅ Jarvis Melhorado inicializado com hotword: '{hotword}'")
        print("🎤 Escutando... (pressione Ctrl+C para sair)")
        print("💡 Diga 'Jarvis' seguido de um comando")
        print("💡 Fale devagar e claramente para melhor reconhecimento")
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
