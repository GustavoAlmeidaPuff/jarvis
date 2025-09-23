#!/bin/bash

# Script para iniciar o Jarvis facilmente

echo "🤖 Iniciando Jarvis - Assistente de Voz Local"
echo "=============================================="

# Verificar se estamos no diretório correto
if [ ! -f "jarvis_assistant.py" ]; then
    echo "❌ Execute este script do diretório do Jarvis"
    exit 1
fi

# Ativar ambiente virtual
if [ -d "jarvis_env" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source jarvis_env/bin/activate
else
    echo "❌ Ambiente virtual não encontrado. Execute install.sh primeiro"
    exit 1
fi

# Carregar configurações
if [ -f ".jarvis_config" ]; then
    echo "⚙️  Carregando configurações..."
    source .jarvis_config
else
    echo "⚠️  Arquivo de configuração não encontrado"
fi

# Verificar chave do Porcupine
if [ -z "$PORCUPINE_ACCESS_KEY" ]; then
    echo "❌ Chave do Porcupine não configurada"
    echo "💡 Configure sua chave em .jarvis_config"
    exit 1
fi

echo "✅ Configuração verificada"
echo "🎤 Iniciando Jarvis..."
echo "💡 Diga 'Jarvis' seguido de um comando"
echo "💡 Pressione Ctrl+C para sair"
echo ""

# Executar Jarvis (versão melhorada)
echo "🚀 Iniciando Jarvis Melhorado..."
python jarvis_improved.py
