#!/usr/bin/env python3
"""
Teste específico para verificar o reconhecimento de voz
"""

import os
import sys
import time
import json
import sounddevice as sd
import numpy as np
import vosk

def test_microphone():
    """Testa se o microfone está funcionando"""
    print("🎤 Testando microfone...")
    print("=" * 30)
    
    try:
        # Configurações de áudio
        sample_rate = 16000
        duration = 3  # segundos
        
        print(f"🎙️  Gravando por {duration} segundos...")
        print("💡 Fale algo agora!")
        
        # Gravar áudio
        audio_data = sd.rec(int(duration * sample_rate), 
                           samplerate=sample_rate, 
                           channels=1, 
                           dtype=np.float32)
        sd.wait()  # Aguardar gravação terminar
        
        # Verificar se capturou algo
        max_amplitude = np.max(np.abs(audio_data))
        print(f"📊 Amplitude máxima capturada: {max_amplitude:.4f}")
        
        if max_amplitude > 0.01:  # Threshold mínimo
            print("✅ Microfone está capturando áudio!")
            return True, audio_data
        else:
            print("❌ Microfone não está capturando áudio suficiente")
            print("💡 Verifique:")
            print("   - Se o microfone está conectado")
            print("   - Se as permissões estão corretas")
            print("   - Se o volume do microfone está alto")
            return False, audio_data
            
    except Exception as e:
        print(f"❌ Erro ao testar microfone: {e}")
        return False, None

def test_vosk_recognition(audio_data):
    """Testa reconhecimento de voz com Vosk"""
    print("\n🗣️  Testando reconhecimento de voz...")
    print("=" * 30)
    
    try:
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
        
        print(f"📁 Usando modelo: {model_path}")
        
        # Inicializar Vosk
        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, 16000)
        
        # Converter áudio para formato correto
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        # Reconhecer
        print("🧠 Processando áudio...")
        
        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result())
            text = result.get('text', '').strip()
            print(f"✅ Texto reconhecido: '{text}'")
            return len(text) > 0
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get('partial', '').strip()
            print(f"⚠️  Reconhecimento parcial: '{partial_text}'")
            return len(partial_text) > 0
            
    except Exception as e:
        print(f"❌ Erro no reconhecimento: {e}")
        return False

def test_audio_levels():
    """Testa níveis de áudio em tempo real"""
    print("\n📊 Testando níveis de áudio em tempo real...")
    print("=" * 30)
    print("💡 Fale por 5 segundos...")
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Status: {status}")
        
        # Calcular nível de áudio
        level = np.max(np.abs(indata))
        if level > 0.01:
            print(f"🎤 Nível: {level:.4f} {'█' * int(level * 50)}")
    
    try:
        with sd.InputStream(samplerate=16000, channels=1, callback=audio_callback):
            time.sleep(5)
        print("✅ Teste de níveis concluído")
        return True
    except Exception as e:
        print(f"❌ Erro no teste de níveis: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🤖 Jarvis - Teste de Reconhecimento de Voz")
    print("=" * 50)
    
    # Teste 1: Microfone
    mic_ok, audio_data = test_microphone()
    
    if not mic_ok:
        print("\n❌ Microfone não está funcionando. Corrija isso primeiro.")
        return False
    
    # Teste 2: Reconhecimento
    if audio_data is not None:
        recognition_ok = test_vosk_recognition(audio_data)
    else:
        recognition_ok = False
    
    # Teste 3: Níveis em tempo real
    levels_ok = test_audio_levels()
    
    print("\n" + "=" * 50)
    print("📊 Resultado dos Testes:")
    print(f"   - Microfone: {'✅' if mic_ok else '❌'}")
    print(f"   - Reconhecimento: {'✅' if recognition_ok else '❌'}")
    print(f"   - Níveis de áudio: {'✅' if levels_ok else '❌'}")
    
    if mic_ok and recognition_ok:
        print("\n🎉 Reconhecimento de voz está funcionando!")
        print("💡 O problema pode ser:")
        print("   - Falar muito baixo")
        print("   - Ruído de fundo")
        print("   - Falar muito rápido")
    elif mic_ok and not recognition_ok:
        print("\n⚠️  Microfone OK, mas reconhecimento falhou")
        print("💡 Tente:")
        print("   - Falar mais devagar")
        print("   - Falar mais alto")
        print("   - Reduzir ruído de fundo")
        print("   - Usar comandos mais simples")
    else:
        print("\n❌ Problemas com microfone")
        print("💡 Verifique configurações de áudio")
    
    return mic_ok and recognition_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
