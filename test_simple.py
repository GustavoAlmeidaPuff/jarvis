#!/usr/bin/env python3
"""
Teste super simples para diagnosticar o problema
"""

import os
import sys
import time
import json
import sounddevice as sd
import numpy as np
import vosk

def test_simple_recognition():
    """Teste simples de reconhecimento"""
    print("🧪 Teste Simples de Reconhecimento")
    print("=" * 40)
    
    # Encontrar modelo Vosk
    model_path = None
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
                    break
            if model_path:
                break
    
    if not model_path:
        print("❌ Modelo Vosk não encontrado")
        return False
    
    print(f"📁 Modelo: {model_path}")
    
    try:
        # Inicializar Vosk
        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, 16000)
        
        print("✅ Vosk inicializado")
        print("🎤 Gravando por 3 segundos...")
        print("💡 Diga apenas: 'teste'")
        
        # Gravar áudio
        duration = 3
        audio_data = sd.rec(int(duration * 16000), 
                           samplerate=16000, 
                           channels=1, 
                           dtype=np.float32)
        sd.wait()
        
        # Converter para formato correto
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        print("🧠 Processando...")
        
        # Reconhecer
        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result())
            text = result.get('text', '').strip().lower()
            print(f"✅ RESULTADO FINAL: '{text}'")
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get('partial', '').strip().lower()
            print(f"⚠️  RESULTADO PARCIAL: '{partial_text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_keywords():
    """Testa palavras-chave específicas"""
    print("\n🔍 Teste de Palavras-Chave")
    print("=" * 30)
    
    keywords = ["teste", "hora", "data", "ajuda"]
    
    for keyword in keywords:
        print(f"💡 Tente dizer: '{keyword}'")
        input("Pressione Enter quando estiver pronto...")
        
        # Gravar
        duration = 2
        audio_data = sd.rec(int(duration * 16000), 
                           samplerate=16000, 
                           channels=1, 
                           dtype=np.float32)
        sd.wait()
        
        # Processar
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        # Reconhecer
        try:
            model_path = os.path.expanduser("~/vosk-models/vosk-model-small-pt-0.3")
            model = vosk.Model(model_path)
            recognizer = vosk.KaldiRecognizer(model, 16000)
            
            if recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(recognizer.Result())
                text = result.get('text', '').strip().lower()
                print(f"🎤 Reconhecido: '{text}'")
                
                if keyword in text:
                    print("✅ SUCESSO!")
                else:
                    print("❌ Não reconheceu corretamente")
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get('partial', '').strip().lower()
                print(f"🎤 Parcial: '{partial_text}'")
                
                if keyword in partial_text:
                    print("✅ SUCESSO PARCIAL!")
                else:
                    print("❌ Não reconheceu")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        print()

def main():
    """Função principal"""
    print("🤖 Teste de Diagnóstico do Jarvis")
    print("=" * 40)
    
    # Teste 1: Reconhecimento simples
    if test_simple_recognition():
        print("\n✅ Teste básico passou!")
        
        # Perguntar se quer testar palavras-chave
        resposta = input("\nQuer testar palavras-chave específicas? (s/n): ")
        if resposta.lower() == 's':
            test_keywords()
    else:
        print("\n❌ Teste básico falhou!")
        print("💡 Verifique se o modelo Vosk está correto")

if __name__ == "__main__":
    main()
