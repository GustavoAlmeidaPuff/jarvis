#!/usr/bin/env python3
"""
Jarvis Manual - Ativação manual (sem Porcupine)
"""

import os
import sys
import time
import logging
import subprocess
import json
import sounddevice as sd
import numpy as np
import vosk

class JarvisManual:
    """Jarvis com ativação manual"""
    
    def __init__(self):
        self.sample_rate = 16000
        self._setup_logging()
        self._init_vosk()
        self._init_commands()
        
        self.logger.info("Jarvis Manual inicializado!")
    
    def _setup_logging(self):
        """Configura logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger('JarvisManual')
    
    def _init_vosk(self):
        """Inicializa Vosk"""
        try:
            model_path = os.path.expanduser("~/vosk-models/vosk-model-small-pt-0.3")
            
            if os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
                self.logger.info(f"✅ Vosk OK - modelo: {model_path}")
            else:
                raise Exception("Modelo Vosk não encontrado")
        except Exception as e:
            self.logger.error(f"❌ Erro Vosk: {e}")
            self.vosk_model = None
            self.vosk_recognizer = None
    
    def _init_commands(self):
        """Inicializa comandos"""
        self.commands = {
            "teste": self._test_command,
            "hora": self._show_time,
            "data": self._show_date,
            "ajuda": self._show_help,
            "navegador": self._open_browser,
            "arquivos": self._list_files
        }
        self.logger.info(f"📋 {len(self.commands)} comandos carregados")
    
    def _recognize_speech(self, audio_data: bytes) -> str:
        """Reconhece fala"""
        if self.vosk_recognizer is None:
            return "teste"
        
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
            self.logger.error(f"Erro reconhecimento: {e}")
            return ""
    
    def _find_command(self, text: str) -> str:
        """Encontra comando"""
        if not text:
            return None
        
        # Busca exata
        if text in self.commands:
            return text
        
        # Busca por palavras
        words = text.split()
        for word in words:
            if word in self.commands:
                return word
        
        return None
    
    def _execute_command(self, command: str):
        """Executa comando"""
        if command in self.commands:
            self.logger.info(f"🚀 EXECUTANDO: {command}")
            try:
                self.commands[command]()
                self.logger.info(f"✅ SUCESSO!")
            except Exception as e:
                self.logger.error(f"❌ ERRO: {e}")
        else:
            self.logger.warning(f"❓ COMANDO DESCONHECIDO: {command}")
    
    def listen_for_command(self):
        """Escuta comando"""
        self.logger.info("🎤 ESCUTANDO COMANDO...")
        self.logger.info("💡 Diga seu comando agora!")
        
        # Gravar por 4 segundos
        duration = 4
        audio_data = sd.rec(int(duration * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=1, 
                           dtype=np.float32)
        sd.wait()
        
        # Converter para formato correto
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        # Reconhecer
        recognized_text = self._recognize_speech(audio_bytes)
        
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
    
    def run(self):
        """Executa loop principal"""
        self.logger.info("🎧 INICIANDO JARVIS MANUAL...")
        
        try:
            while True:
                print("\n" + "="*50)
                print("🤖 Jarvis Manual - Ativação Manual")
                print("="*50)
                print("💡 Comandos disponíveis:")
                for cmd in sorted(self.commands.keys()):
                    print(f"   - {cmd}")
                print()
                print("Opções:")
                print("   ENTER - Escutar comando")
                print("   q - Sair")
                print()
                
                choice = input("Pressione ENTER para escutar ou 'q' para sair: ").strip().lower()
                
                if choice == "q":
                    break
                else:
                    self.listen_for_command()
                    
        except KeyboardInterrupt:
            self.logger.info("👋 PARANDO...")
    
    # Comandos
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
    print("🤖 Jarvis Manual - Ativação Manual")
    print("=" * 40)
    
    try:
        jarvis = JarvisManual()
        jarvis.run()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
