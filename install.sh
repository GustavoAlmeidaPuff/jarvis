#!/bin/bash

# Script de instalação automatizada do Jarvis
# Compatível com Ubuntu/Debian/Linux Mint

set -e

echo "🤖 Instalando Jarvis - Assistente de Voz Local"
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
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

# Verificar sistema operacional
if ! command -v apt &> /dev/null; then
    print_error "Este script é compatível apenas com sistemas baseados em Debian/Ubuntu"
    exit 1
fi

print_status "Atualizando lista de pacotes..."
sudo apt update

print_status "Instalando dependências do sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    portaudio19-dev \
    alsa-utils \
    wget \
    unzip \
    curl

print_status "Instalando dependências Python..."
pip3 install --user -r requirements.txt

# Verificar se pip3 install funcionou
if [ $? -ne 0 ]; then
    print_error "Falha ao instalar dependências Python"
    exit 1
fi

print_status "Configurando permissões de áudio..."
sudo usermod -a -G audio $USER

print_status "Criando diretório para modelos Vosk..."
mkdir -p ~/vosk-models

print_status "Baixando modelo Vosk em português..."
cd ~/vosk-models
if [ ! -d "vosk-model-small-pt-0.3" ]; then
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
    unzip -q vosk-model-small-pt-0.3.zip
    rm vosk-model-small-pt-0.3.zip
    print_status "Modelo Vosk baixado com sucesso!"
else
    print_warning "Modelo Vosk já existe, pulando download..."
fi

# Voltar ao diretório do projeto
cd - > /dev/null

print_status "Criando arquivo de configuração..."
cat > ~/.jarvis_config << EOF
# Configuração do Jarvis
export PORCUPINE_ACCESS_KEY=""
export JARVIS_MODEL_PATH="$HOME/vosk-models/vosk-model-small-pt-0.3"
EOF

print_status "Tornando o script executável..."
chmod +x jarvis_assistant.py

print_status "Testando instalação..."
python3 -c "import pvporcupine, vosk, sounddevice, numpy; print('✅ Todas as dependências estão instaladas!')"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Instalação concluída com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Configure sua chave do Porcupine:"
    echo "   nano ~/.jarvis_config"
    echo "   # Adicione sua chave em PORCUPINE_ACCESS_KEY"
    echo ""
    echo "2. Recarregue suas configurações:"
    echo "   source ~/.jarvis_config"
    echo ""
    echo "3. Execute o Jarvis:"
    echo "   python3 jarvis_assistant.py"
    echo ""
    echo "💡 Para mais informações, consulte o README.md"
else
    print_error "Falha no teste de instalação"
    exit 1
fi
