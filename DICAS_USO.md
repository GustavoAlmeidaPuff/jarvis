# 💡 Dicas para Usar o Jarvis

## 🎤 Como Falar com o Jarvis

### 1. Sequência Correta
1. **Diga "Jarvis"** (aguarde confirmação)
2. **Aguarde 1 segundo** (para o sistema se preparar)
3. **Fale seu comando** devagar e claramente
4. **Aguarde execução**

### 2. Dicas de Pronúncia
- ✅ **Fale devagar** - não tenha pressa
- ✅ **Fale claramente** - articule bem as palavras
- ✅ **Use volume normal** - nem muito alto, nem muito baixo
- ✅ **Reduza ruído** - ambiente mais silencioso ajuda
- ✅ **Pause entre palavras** - "abrir... navegador"

### 3. Comandos que Funcionam Melhor
**Comandos Simples (mais fáceis de reconhecer):**
- `mostrar hora`
- `mostrar data`
- `abrir navegador`
- `ajuda`

**Comandos Mais Complexos:**
- `abrir firefox` (pode ser reconhecido como "abrir navegador")
- `status sistema` (pode ser reconhecido como "ajuda")

### 4. Solução de Problemas

**Se o Jarvis não reconhece:**
1. **Fale mais devagar** - o Vosk precisa de tempo para processar
2. **Use comandos mais simples** - menos palavras = melhor reconhecimento
3. **Verifique o ambiente** - menos ruído de fundo
4. **Teste com demo** - `python demo.py` para testar comandos

**Se reconhece mas não executa:**
1. **Verifique se a aplicação está instalada** (ex: Firefox, Chrome)
2. **Consulte os logs** em `jarvis.log`
3. **Use comandos exatos** da lista disponível

### 5. Comandos Recomendados para Teste

**Comece com estes (mais fáceis):**
```
Jarvis, mostrar hora
Jarvis, mostrar data  
Jarvis, ajuda
Jarvis, teste
```

**Depois tente estes:**
```
Jarvis, abrir navegador
Jarvis, listar arquivos
Jarvis, status sistema
```

### 6. Timing Perfeito

**Sequência ideal:**
1. "Jarvis" → ⏱️ Aguarde confirmação
2. Pausa de 1 segundo
3. "mostrar hora" → ⏱️ Aguarde processamento
4. Aguarde execução

**Tempo total:** ~4-5 segundos por comando

### 7. Ambiente Ideal

**Para melhor reconhecimento:**
- 🏠 **Ambiente silencioso** - sem TV, música, etc.
- 📍 **Distância adequada** - 30-50cm do microfone
- 🎙️ **Microfone limpo** - sem obstruções
- 🔇 **Sem eco** - evite ambientes muito reverberantes

---

**💡 Lembre-se: O reconhecimento melhora com a prática!**
**🎯 Comece com comandos simples e vá evoluindo gradualmente.**
