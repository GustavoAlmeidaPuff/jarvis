# 🔧 Solução de Problemas - Jarvis

## 🚨 Problema Atual: Comandos Não Reconhecidos

**Sintomas:**
- ✅ Hotword "Jarvis" é detectada
- ❌ Comandos não são reconhecidos
- ❌ Log mostra "Nenhum comando reconhecido"

## 🔍 Diagnóstico Passo a Passo

### 1. Teste Básico de Reconhecimento
```bash
python test_simple.py
```
- Diga apenas "teste" quando solicitado
- Veja se o Vosk consegue reconhecer

### 2. Teste com Jarvis Simples
```bash
python jarvis_simple.py
```
- Comandos mais simples: teste, hora, data
- Melhor feedback visual

### 3. Verificar Modelo Vosk
```bash
ls -la ~/vosk-models/
```
- Deve mostrar: `vosk-model-small-pt-0.3`

## 💡 Soluções Possíveis

### Solução 1: Falar Mais Devagar
- **Problema**: Falando muito rápido
- **Solução**: Pause entre palavras
- **Exemplo**: "Jarvis" → pausa → "tes-te" (devagar)

### Solução 2: Usar Comandos Mais Simples
- **Em vez de**: "mostrar hora"
- **Use**: "hora"
- **Em vez de**: "abrir navegador"  
- **Use**: "navegador"

### Solução 3: Verificar Ambiente
- **Ruído**: Ambiente muito barulhento?
- **Distância**: Muito longe do microfone?
- **Volume**: Muito baixo ou alto?

### Solução 4: Testar com Demo
```bash
python demo.py
```
- Teste comandos sem microfone
- Confirme que os comandos funcionam

## 🎯 Comandos Recomendados para Teste

**Ordem de facilidade:**
1. `Jarvis, teste` (mais fácil)
2. `Jarvis, hora`
3. `Jarvis, data`
4. `Jarvis, ajuda`

## 🔧 Scripts de Diagnóstico

### Teste Completo
```bash
python test_voice_recognition.py
```

### Teste Simples
```bash
python test_simple.py
```

### Jarvis Simples
```bash
python jarvis_simple.py
```

## 📋 Checklist de Verificação

- [ ] Hotword "Jarvis" é detectada?
- [ ] Modelo Vosk está instalado?
- [ ] Microfone está funcionando?
- [ ] Ambiente está silencioso?
- [ ] Falando devagar e claro?
- [ ] Usando comandos simples?

## 🆘 Se Nada Funcionar

### Opção 1: Usar Demo Interativa
```bash
python demo.py
```
- Digite comandos no terminal
- Teste sem microfone

### Opção 2: Verificar Logs
```bash
tail -f jarvis.log
```
- Veja mensagens de erro detalhadas

### Opção 3: Reinstalar Modelo Vosk
```bash
rm -rf ~/vosk-models/vosk-model-small-pt-0.3
cd ~/vosk-models
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
```

## 💬 Dicas Importantes

1. **Paciência**: Reconhecimento melhora com prática
2. **Consistência**: Use sempre os mesmos comandos
3. **Ambiente**: Ambiente silencioso é crucial
4. **Timing**: Aguarde confirmação antes de falar comando

---

**🎯 Foco: Comece com `Jarvis, teste` - é o comando mais simples!**
