# 🔑 Como Configurar a Chave do Porcupine

## 📋 Passo a Passo

### 1. Obter Chave de Acesso Gratuita
1. Acesse: https://console.picovoice.ai/
2. Clique em "Sign Up" para criar uma conta gratuita
3. Faça login na sua conta
4. Vá para a seção "Access Keys"
5. Clique em "Create Access Key"
6. Copie a chave gerada

### 2. Configurar a Chave no Sistema

**Opção A: Configuração Temporária (para teste)**
```bash
export PORCUPINE_ACCESS_KEY="sua_chave_aqui"
```

**Opção B: Configuração Permanente**
```bash
# Adicionar ao arquivo de configuração do shell
echo 'export PORCUPINE_ACCESS_KEY="sua_chave_aqui"' >> ~/.bashrc
source ~/.bashrc
```

**Opção C: Arquivo de Configuração**
```bash
# Criar arquivo de configuração
cp config_example.env ~/.jarvis_config
nano ~/.jarvis_config
# Adicione sua chave na linha PORCUPINE_ACCESS_KEY
```

### 3. Testar Configuração

```bash
# Ativar ambiente virtual
source jarvis_env/bin/activate

# Testar hotword personalizada
python test_custom_hotword.py

# Testar instalação completa
python test_installation.py
```

### 4. Executar Jarvis

```bash
# Com hotword personalizada
python jarvis_assistant.py

# Ou com modelo Vosk específico
python jarvis_assistant.py ~/vosk-models/vosk-model-small-pt-0.3
```

## ✅ Verificação

Se tudo estiver configurado corretamente, você verá:
- ✅ Hotword personalizada funcionando
- ✅ Porcupine inicializado com sucesso
- ✅ Jarvis pronto para escutar comandos

## 🆘 Solução de Problemas

**Erro: "Chave de acesso não configurada"**
- Verifique se a variável está definida: `echo $PORCUPINE_ACCESS_KEY`
- Recarregue o shell: `source ~/.bashrc`

**Erro: "Invalid access key"**
- Verifique se copiou a chave corretamente
- Gere uma nova chave no console Picovoice

**Erro: "Hotword personalizada não encontrada"**
- Verifique se o arquivo `jarvis_custom.ppn` está no diretório
- Execute: `ls -la jarvis_custom.ppn`

## 💡 Dicas

- A chave gratuita permite até 3 dispositivos
- Hotwords personalizadas são mais precisas que as padrão
- Você pode criar múltiplas hotwords no Picovoice Console
- A chave é válida por 1 ano (renovação gratuita)

---
**Com sua hotword personalizada, o Jarvis será ainda mais preciso! 🎯**
