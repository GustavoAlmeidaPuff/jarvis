#!/usr/bin/env python3
"""
Demonstração do Jarvis - Mostra como funciona sem precisar de microfone
"""

import os
import sys
import time
import logging
import subprocess
import json
from typing import Dict, Callable, Optional
import vosk
from pathlib import Path


class JarvisDemo:
    """Demonstração do assistente Jarvis"""
    
    def __init__(self, model_path: str = None):
        """
        Inicializa a demonstração
        
        Args:
            model_path: Caminho para o modelo Vosk (opcional)
        """
        self.hotword = "jarvis"
        
        # Configuração de logging
        self._setup_logging()
        
        # Inicialização dos componentes
        self._init_vosk(model_path)
        self._init_command_mapping()
        
        self.logger.info("Jarvis Demo inicializado com sucesso!")
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('JarvisDemo')
    
    def _init_vosk(self, model_path: str = None):
        """Inicializa o Vosk para reconhecimento de voz"""
        try:
            if model_path is None:
                # Tentar encontrar o modelo padrão
                model_path = self._find_vosk_model()
            
            if model_path and os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                self.logger.info(f"✅ Vosk inicializado com modelo: {model_path}")
                self.vosk_available = True
            else:
                self.logger.warning("⚠️  Modelo Vosk não encontrado. Usando modo simulado.")
                self.vosk_model = None
                self.vosk_available = False
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Vosk: {e}")
            self.vosk_model = None
            self.vosk_available = False
    
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
        
        self.logger.info(f"📋 Mapeamento de comandos inicializado com {len(self.commands)} comandos")
    
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
            self.logger.info(f"🚀 Executando comando: {command}")
            try:
                self.commands[command]()
            except Exception as e:
                self.logger.error(f"❌ Erro ao executar comando '{command}': {e}")
        else:
            self.logger.warning(f"⚠️  Comando não reconhecido: {command}")
    
    def simulate_command(self, text: str):
        """Simula execução de comando"""
        self.logger.info(f"🎤 Texto reconhecido: '{text}'")
        
        # Encontra e executa o comando
        command = self._find_best_command_match(text)
        if command:
            self._execute_command(command)
        else:
            self.logger.info("❓ Comando não reconhecido")
            self.logger.info("💡 Comandos disponíveis:")
            for cmd in sorted(self.commands.keys()):
                print(f"   - {cmd}")
    
    def run_demo(self):
        """Executa a demonstração interativa"""
        print("\n🤖 Jarvis - Demonstração Interativa")
        print("=" * 50)
        print("💡 Digite comandos para testar o Jarvis")
        print("💡 Digite 'help' para ver comandos disponíveis")
        print("💡 Digite 'quit' para sair")
        print()
        
        while True:
            try:
                user_input = input("🎤 Digite um comando: ").strip().lower()
                
                if user_input == "quit" or user_input == "exit":
                    break
                elif user_input == "help":
                    self._show_help()
                elif user_input == "status":
                    self._show_status()
                elif user_input:
                    self.simulate_command(user_input)
                
                print()  # Linha em branco para separar
                
            except KeyboardInterrupt:
                print("\n👋 Demonstração encerrada pelo usuário")
                break
            except EOFError:
                break
    
    def _show_status(self):
        """Mostra status do sistema"""
        self.logger.info("📊 Status do Jarvis:")
        print(f"   - Vosk disponível: {'✅' if self.vosk_available else '❌'}")
        print(f"   - Comandos configurados: {len(self.commands)}")
        print(f"   - Modelo Vosk: {self.vosk_model.path if self.vosk_model else 'Não encontrado'}")
    
    # Comandos do sistema
    def _open_browser(self):
        """Abre o navegador padrão"""
        self.logger.info("🌐 Abrindo navegador...")
        subprocess.run(["xdg-open", "https://www.google.com"], check=False)
    
    def _open_firefox(self):
        """Abre o Firefox"""
        self.logger.info("🦊 Abrindo Firefox...")
        subprocess.run(["firefox"], check=False)
    
    def _open_chrome(self):
        """Abre o Chrome"""
        self.logger.info("🌍 Abrindo Chrome...")
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
        self.logger.info("💻 Abrindo VSCode...")
        subprocess.run(["code"], check=False)
    
    def _open_terminal(self):
        """Abre um terminal"""
        self.logger.info("🖥️  Abrindo terminal...")
        subprocess.run(["gnome-terminal"], check=False)
    
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
        print("\n💡 Comandos de controle:")
        print("   - help (mostra esta ajuda)")
        print("   - status (mostra status)")
        print("   - quit/exit (sair)")


def main():
    """Função principal"""
    print("🤖 Jarvis - Demonstração")
    print("=" * 30)
    
    # Verificar se há argumentos de linha de comando
    model_path = None
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    try:
        # Cria e inicializa a demonstração
        demo = JarvisDemo(model_path=model_path)
        
        # Executa demonstração
        demo.run_demo()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
