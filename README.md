# 🤖 Jarvis - Assistente de Voz Local

Um assistente de voz simples que roda localmente no Linux, similar à Alexa, mas sem depender de serviços externos. O Jarvis fica ouvindo continuamente o microfone e responde quando você diz a palavra de ativação seguida de um comando.

## ✨ Características

- **100% Offline**: Funciona sem conexão com a internet
- **Detecção de Hotword**: Usa Porcupine (Picovoice) para detectar "Jarvis"
- **Reconhecimento de Voz**: Usa Vosk para converter fala em texto
- **Comandos Personalizáveis**: Sistema flexível de mapeamento de comandos
- **Logs Detalhados**: Sistema completo de logging para depuração
- **Responsivo**: Interface simples e eficiente

## 🚀 Instalação Rápida

### 1. Instalar Dependências do Sistema

```bash
# Ubuntu/Debian/Linux Mint
sudo apt update
sudo apt install python3 python3-pip portaudio19-dev python3-dev

# Para VSCode (opcional)
sudo apt install code

# Para Firefox (opcional)
sudo apt install firefox

# Para Chrome (opcional)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

### 2. Instalar Dependências Python

```bash
# Instalar dependências
pip3 install -r requirements.txt

# Ou instalar individualmente:
pip3 install pvporcupine vosk sounddevice numpy scipy pyaudio
```

### 3. Configurar Porcupine (Picovoice)

O Porcupine requer uma chave de acesso gratuita:

1. Acesse [Picovoice Console](https://console.picovoice.ai/)
2. Crie uma conta gratuita
3. Obtenha sua chave de acesso
4. Configure a variável de ambiente:

```bash
export PORCUPINE_ACCESS_KEY="sua_chave_aqui"
```

**Ou** adicione ao seu `~/.bashrc`:
```bash
echo 'export PORCUPINE_ACCESS_KEY="sua_chave_aqui"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Baixar Modelo Vosk (Opcional)

Para melhor reconhecimento de voz em português:

```bash
# Criar diretório para modelos
mkdir -p ~/vosk-models

# Baixar modelo em português (recomendado)
cd ~/vosk-models
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip

# Ou modelo em inglês (menor)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

## 🎯 Como Usar

### Execução Básica

```bash
# Executar com configurações padrão
python3 jarvis_assistant.py

# Executar com hotword personalizada
python3 jarvis_assistant.py "hey jarvis"

# Executar com modelo Vosk específico
python3 jarvis_assistant.py "jarvis" ~/vosk-models/vosk-model-small-pt-0.3
```

### Comandos Disponíveis

Diga **"Jarvis"** seguido de um destes comandos:

| Comando | Ação |
|---------|------|
| `teste` | Testa se o Jarvis está funcionando |
| `hora` | Mostra a hora atual |
| `data` | Mostra a data atual |
| `ajuda` | Lista todos os comandos disponíveis |
| `navegador` | Abre o navegador Chrome |
| `arquivos` | Lista arquivos do diretório atual |
| `status` | Mostra status do sistema |
| `olá` | Saudação personalizada |
| `trabalho` | Abre aplicativos de trabalho |
| `desliga` | Desliga o computador completamente |

### Exemplo de Uso

1. Execute o programa: `python3 jarvis_assistant.py`
2. Aguarde a mensagem "🎤 Escutando..."
3. Diga: **"Jarvis, mostrar hora"**
4. O programa detectará a hotword e executará o comando

## 🔧 Configuração Avançada

### Personalizando Comandos

Edite o arquivo `jarvis_assistant.py` na função `_init_command_mapping()`:

```python
self.commands = {
    "seu comando": self._sua_funcao,
    # ... outros comandos
}
```

E implemente a função correspondente:

```python
def _sua_funcao(self):
    """Descrição do seu comando"""
    subprocess.run(["seu", "comando", "aqui"], check=False)
```

### Configurando Hotword Personalizada

Para usar uma hotword personalizada no Porcupine:

1. Acesse [Picovoice Console](https://console.picovoice.ai/)
2. Vá em "Porcupine" → "Create Custom Keyword"
3. Grave sua palavra de ativação
4. Baixe o arquivo `.ppn`
5. Modifique o código para usar o arquivo personalizado:

```python
self.porcupine = pvporcupine.create(
    access_key=os.getenv('PORCUPINE_ACCESS_KEY', ''),
    keyword_paths=['caminho/para/sua/hotword.ppn']
)
```

### Ajustando Sensibilidade de Áudio

Modifique as configurações de áudio na classe `JarvisAssistant`:

```python
# Aumentar sensibilidade (detectar sons mais baixos)
self.sample_rate = 22050  # Maior taxa de amostragem

# Ajustar tamanho do chunk para melhor detecção
self.chunk_size = 512  # Chunks menores = mais responsivo
```

## 🐛 Solução de Problemas

### Erro: "No module named 'pvporcupine'"

```bash
pip3 install pvporcupine
```

### Erro: "ALSA lib pcm.c:2565:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear"

```bash
# Instalar ALSA utils
sudo apt install alsa-utils

# Testar áudio
speaker-test -t wav -c 2
```

### Erro: "Permission denied" no microfone

```bash
# Adicionar usuário ao grupo audio
sudo usermod -a -G audio $USER

# Reiniciar sessão ou fazer logout/login
```

### Jarvis não detecta a hotword

1. Verifique se a chave do Porcupine está configurada
2. Teste o microfone: `arecord -f cd -d 5 test.wav`
3. Ajuste o volume do microfone
4. Fale mais próximo ao microfone
5. Verifique os logs em `jarvis.log`

### Reconhecimento de voz ruim

1. Baixe um modelo Vosk maior e mais preciso
2. Fale mais devagar e claramente
3. Reduza ruído de fundo
4. Use comandos mais simples

## 📁 Estrutura do Projeto

```
jarvis/
├── jarvis_assistant.py    # Aplicativo principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── jarvis.log            # Logs do sistema (gerado automaticamente)
└── vosk-models/          # Modelos Vosk (opcional)
```

## 🔒 Segurança

- **Comandos Seguros**: Usa `subprocess.run()` ao invés de `os.system()`
- **Validação**: Comandos são mapeados previamente, não executados diretamente
- **Logs**: Todas as ações são registradas para auditoria
- **Permissões**: Requer permissões mínimas do sistema

## 🚀 Executando como Daemon

Para executar o Jarvis em background:

```bash
# Usando nohup
nohup python3 jarvis_assistant.py > jarvis.out 2>&1 &

# Usando screen
screen -S jarvis
python3 jarvis_assistant.py
# Ctrl+A, D para sair do screen

# Usando systemd (criar serviço)
sudo cp jarvis.service /etc/systemd/system/
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

## 📝 Logs

Os logs são salvos em:
- **Arquivo**: `jarvis.log`
- **Console**: Saída em tempo real
- **Nível**: INFO (configurável)

Exemplo de log:
```
2024-01-15 10:30:15 - Jarvis - INFO - Jarvis inicializado com sucesso!
2024-01-15 10:30:20 - Jarvis - INFO - Hotword 'jarvis' detectada!
2024-01-15 10:30:21 - Jarvis - INFO - Texto reconhecido: 'mostrar hora'
2024-01-15 10:30:21 - Jarvis - INFO - Executando comando: mostrar hora
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs em `jarvis.log`
2. Consulte a seção de solução de problemas
3. Abra uma issue no GitHub
4. Verifique se todas as dependências estão instaladas

---

**Desenvolvido com ❤️ para a comunidade Linux**
