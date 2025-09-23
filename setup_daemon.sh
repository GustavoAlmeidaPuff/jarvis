#!/bin/bash

# Script para configurar Jarvis como serviço systemd

set -e

echo "🔧 Configurando Jarvis como serviço systemd"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se é root
if [[ $EUID -eq 0 ]]; then
   print_error "Este script não deve ser executado como root!"
   exit 1
fi

# Obter diretório atual
JARVIS_DIR=$(pwd)
USERNAME=$(whoami)

print_status "Configurando serviço para usuário: $USERNAME"
print_status "Diretório do Jarvis: $JARVIS_DIR"

# Criar arquivo de serviço personalizado
print_status "Criando arquivo de serviço..."
cat > jarvis_user.service << EOF
[Unit]
Description=Jarvis Voice Assistant
After=network.target sound.target
Wants=sound.target

[Service]
Type=simple
User=$USERNAME
Group=audio
WorkingDirectory=$JARVIS_DIR
ExecStart=/usr/bin/python3 $JARVIS_DIR/jarvis_assistant.py
Restart=always
RestartSec=10
Environment=DISPLAY=:0
Environment=PULSE_RUNTIME_PATH=/run/user/$(id -u)/pulse
EnvironmentFile=/home/$USERNAME/.jarvis_config

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=jarvis

# Segurança
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$JARVIS_DIR

[Install]
WantedBy=multi-user.target
EOF

# Copiar arquivo de serviço
print_status "Instalando arquivo de serviço..."
sudo cp jarvis_user.service /etc/systemd/system/jarvis.service

# Recarregar systemd
print_status "Recarregando systemd..."
sudo systemctl daemon-reload

# Habilitar serviço
print_status "Habilitando serviço Jarvis..."
sudo systemctl enable jarvis.service

print_status "Configuração concluída!"
echo ""
echo "📋 Comandos úteis:"
echo "  Iniciar:     sudo systemctl start jarvis"
echo "  Parar:       sudo systemctl stop jarvis"
echo "  Status:      sudo systemctl status jarvis"
echo "  Logs:        sudo journalctl -u jarvis -f"
echo "  Reiniciar:   sudo systemctl restart jarvis"
echo ""
echo "⚠️  Lembre-se de configurar sua chave do Porcupine em ~/.jarvis_config"
echo ""

# Limpar arquivo temporário
rm jarvis_user.service

print_status "Para iniciar o serviço agora, execute:"
echo "  sudo systemctl start jarvis"
