#!/usr/bin/env python3
"""
Versão de teste do Jarvis que funciona sem chave do Porcupine
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
import vosk
from pathlib import Path


class JarvisTestAssistant:
    """Versão de teste do assistente Jarvis"""
    
    def __init__(self, model_path: str = None):
        """
        Inicializa o assistente em modo de teste
        
        Args:
            model_path: Caminho para o modelo Vosk (opcional)
        """
        self.hotword = "jarvis"
        self.is_listening = False
        self.is_processing_command = False
        
        # Configuração de áudio
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        
        # Configuração de logging
        self._setup_logging()
        
        # Inicialização dos componentes
        self._init_vosk(model_path)
        self._init_command_mapping()
        
        self.logger.info("Jarvis (modo teste) inicializado com sucesso!")
        self.logger.info("⚠️  Modo de teste: Digite 'jarvis' no terminal para simular hotword")
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jarvis_test.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('JarvisTest')
    
    def _init_vosk(self, model_path: str = None):
        """Inicializa o Vosk para reconhecimento de voz"""
        try:
            if model_path is None:
                # Tentar encontrar o modelo padrão
                model_path = self._find_vosk_model()
            
            if model_path and os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
                self.logger.info(f"Vosk inicializado com modelo: {model_path}")
            else:
                self.logger.warning("Modelo Vosk não encontrado. Usando modo de teste.")
                self.vosk_model = None
                self.vosk_recognizer = None
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Vosk: {e}")
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
            "listar arquivos": self._list_files,
            "status sistema": self._system_status,
            "ajuda": self._show_help,
            "teste": self._test_command
        }
        
        self.logger.info(f"Mapeamento de comandos inicializado com {len(self.commands)} comandos")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback para captura de áudio"""
        if status:
            self.logger.warning(f"Status de áudio: {status}")
        
        # Converte para int16 e adiciona à fila
        audio_data = (indata[:, 0] * 32767).astype(np.int16)
        self.audio_queue.put(audio_data.tobytes())
    
    def _recognize_speech(self, audio_data: bytes) -> str:
        """Reconhece fala usando Vosk"""
        if self.vosk_recognizer is None:
            # Modo de teste - retorna comando simulado
            return "mostrar hora"
        
        try:
            if self.vosk_recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.vosk_recognizer.Result())
                return result.get('text', '').strip().lower()
            else:
                partial = json.loads(self.vosk_recognizer.PartialResult())
                return partial.get('partial', '').strip().lower()
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
        
        # Busca por palavras-chave
        recognized_words = set(recognized_text.split())
        
        best_match = None
        best_score = 0
        
        for command in self.commands.keys():
            command_words = set(command.split())
            
            # Calcula similaridade baseada em palavras em comum
            common_words = recognized_words.intersection(command_words)
            score = len(common_words) / len(command_words)
            
            if score > best_score and score >= 0.5:  # Pelo menos 50% de similaridade
                best_match = command
                best_score = score
        
        return best_match
    
    def _execute_command(self, command: str):
        """Executa o comando correspondente"""
        if command in self.commands:
            self.logger.info(f"Executando comando: {command}")
            try:
                self.commands[command]()
            except Exception as e:
                self.logger.error(f"Erro ao executar comando '{command}': {e}")
        else:
            self.logger.warning(f"Comando não reconhecido: {command}")
    
    def _listen_for_command(self):
        """Escuta por comandos após detecção da hotword"""
        self.logger.info("Escutando comando...")
        self.is_processing_command = True
        
        # Coleta áudio por 3 segundos
        command_audio = b""
        start_time = time.time()
        
        while time.time() - start_time < 3.0:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                command_audio += audio_data
            except queue.Empty:
                continue
        
        # Reconhece o comando
        recognized_text = self._recognize_speech(command_audio)
        self.logger.info(f"Texto reconhecido: '{recognized_text}'")
        
        # Encontra e executa o comando
        command = self._find_best_command_match(recognized_text)
        if command:
            self._execute_command(command)
        else:
            self.logger.info("Comando não reconhecido")
        
        self.is_processing_command = False
    
    def simulate_hotword(self):
        """Simula detecção de hotword para teste"""
        self.logger.info("🔥 Hotword simulada detectada!")
        self._listen_for_command()
    
    def start_listening(self):
        """Inicia o loop principal de escuta"""
        self.logger.info("Iniciando escuta contínua...")
        self.logger.info("💡 Digite 'jarvis' no terminal para simular hotword")
        self.is_listening = True
        
        # Thread para captura de áudio
        def audio_thread():
            try:
                with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype=np.float32,
                    blocksize=self.chunk_size,
                    callback=self._audio_callback
                ):
                    while self.is_listening:
                        time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Erro no thread de áudio: {e}")
        
        # Iniciar thread de áudio
        audio_thread_obj = threading.Thread(target=audio_thread)
        audio_thread_obj.daemon = True
        audio_thread_obj.start()
        
        # Loop principal para simulação de hotword
        try:
            while self.is_listening:
                user_input = input().strip().lower()
                if user_input == "jarvis" and not self.is_processing_command:
                    self.simulate_hotword()
                elif user_input == "quit" or user_input == "exit":
                    break
                elif user_input == "help":
                    self._show_help()
                elif user_input == "status":
                    self.logger.info(f"Status: Escutando={self.is_listening}, Processando={self.is_processing_command}")
                    
        except KeyboardInterrupt:
            self.logger.info("Interrompido pelo usuário")
        finally:
            self.stop_listening()
    
    def stop_listening(self):
        """Para a escuta"""
        self.is_listening = False
        self.logger.info("Escuta interrompida")
    
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
            self.logger.info(f"Hora atual: {result.stdout.strip()}")
    
    def _show_date(self):
        """Mostra a data atual"""
        result = subprocess.run(["date"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"Data atual: {result.stdout.strip()}")
    
    def _open_vscode(self):
        """Abre o VSCode"""
        subprocess.run(["code"], check=False)
    
    def _open_terminal(self):
        """Abre um terminal"""
        subprocess.run(["gnome-terminal"], check=False)
    
    def _list_files(self):
        """Lista arquivos do diretório atual"""
        result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info("Arquivos no diretório atual:")
            print(result.stdout)
    
    def _system_status(self):
        """Mostra status do sistema"""
        result = subprocess.run(["uptime"], capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"Status do sistema: {result.stdout.strip()}")
    
    def _test_command(self):
        """Comando de teste"""
        self.logger.info("🧪 Comando de teste executado com sucesso!")
    
    def _show_help(self):
        """Mostra comandos disponíveis"""
        self.logger.info("Comandos disponíveis:")
        for command in sorted(self.commands.keys()):
            print(f"  - {command}")
        print("\nComandos de controle:")
        print("  - jarvis (simula hotword)")
        print("  - help (mostra esta ajuda)")
        print("  - status (mostra status)")
        print("  - quit/exit (sair)")


def main():
    """Função principal"""
    print("🤖 Jarvis - Assistente de Voz Local (MODO TESTE)")
    print("=" * 50)
    
    # Verificar se há argumentos de linha de comando
    model_path = None
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    try:
        # Cria e inicializa o assistente
        jarvis = JarvisTestAssistant(model_path=model_path)
        
        print(f"✅ Jarvis inicializado em modo de teste")
        print("🎤 Escutando... (digite 'jarvis' para simular hotword)")
        print("💡 Digite 'help' para ver comandos disponíveis")
        print("💡 Digite 'quit' para sair")
        print()
        
        # Inicia a escuta
        jarvis.start_listening()
        
    except KeyboardInterrupt:
        print("\n👋 Jarvis encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
