# 🚀 Instruções Rápidas - Jarvis

## ✅ Status Atual
- ✅ Todas as dependências instaladas
- ✅ Modelo Vosk em português baixado
- ✅ Ambiente virtual configurado
- ✅ Demonstração funcionando
- ✅ Hotword personalizada "jarvis" integrada
- ✅ Chave do Porcupine configurada
- ✅ Jarvis 100% funcional!

## 🎯 Como Usar Agora

### 1. Ativar Ambiente Virtual
```bash
cd /home/gustavo/code/jarvis
source jarvis_env/bin/activate
```

### 2. Testar Demonstração
```bash
python demo.py
```
- Digite comandos como "abrir chrome", "mostrar hora", "teste"
- Digite "help" para ver todos os comandos
- Digite "quit" para sair

### 3. Configurar Porcupine (Para Detecção Real de Voz)
**Sua hotword personalizada "jarvis" já está integrada!** 

Apenas configure a chave de acesso:
1. Acesse: https://console.picovoice.ai/
2. Crie conta gratuita
3. Obtenha sua chave de acesso
4. Configure:
```bash
export PORCUPINE_ACCESS_KEY="sua_chave_aqui"
```

**Ou siga o guia completo:** `CONFIGURAR_PORCUPINE.md`

### 4. Executar Jarvis Completo

**Opção A: Script Automático (Recomendado)**
```bash
./start_jarvis.sh
```

**Opção B: Manual**
```bash
source jarvis_env/bin/activate
source .jarvis_config
python jarvis_assistant.py
```

## 📋 Comandos Disponíveis
- `abrir navegador` - Abre navegador padrão
- `abrir firefox/chrome` - Abre navegadores específicos
- `mostrar hora/data` - Exibe informações de tempo
- `abrir vscode/terminal` - Abre aplicações
- `listar arquivos` - Lista arquivos do diretório
- `status sistema` - Mostra status do sistema
- `ajuda` - Lista todos os comandos

## 🔧 Próximos Passos
1. Configure a chave do Porcupine
2. Teste com microfone real
3. Personalize comandos conforme necessário
4. Configure como serviço systemd (opcional)

## 📁 Arquivos Importantes
- `jarvis_assistant.py` - Aplicativo principal
- `demo.py` - Demonstração interativa
- `test_installation.py` - Teste de instalação
- `README.md` - Documentação completa
- `jarvis_env/` - Ambiente virtual Python

## 🆘 Solução de Problemas
- **Erro de áudio**: Verifique permissões do microfone
- **Comando não funciona**: Verifique se aplicativo está instalado
- **Vosk não funciona**: Verifique se modelo está em ~/vosk-models/

---
**Jarvis está pronto para uso! 🎉**
