#!/usr/bin/env python3
"""
Script de teste para verificar se todas as dependências estão instaladas corretamente
"""

import sys
import os

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("🧪 Testando instalação do Jarvis...")
    print("=" * 40)
    
    tests = [
        ("pvporcupine", "Porcupine (detecção de hotword)"),
        ("vosk", "Vosk (reconhecimento de voz)"),
        ("sounddevice", "SoundDevice (captura de áudio)"),
        ("numpy", "NumPy (processamento numérico)"),
        ("scipy", "SciPy (processamento de sinal)"),
        ("pyaudio", "PyAudio (interface de áudio)")
    ]
    
    all_passed = True
    
    for module, description in tests:
        try:
            __import__(module)
            print(f"✅ {description}: OK")
        except ImportError as e:
            print(f"❌ {description}: FALHOU - {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 Todas as dependências estão instaladas!")
        print("✅ Jarvis está pronto para uso!")
    else:
        print("❌ Algumas dependências estão faltando.")
        print("💡 Execute: pip3 install -r requirements.txt")
        return False
    
    return True

def test_audio_devices():
    """Testa se há dispositivos de áudio disponíveis"""
    print("\n🎤 Testando dispositivos de áudio...")
    print("=" * 40)
    
    try:
        import sounddevice as sd
        
        # Listar dispositivos de entrada
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if input_devices:
            print(f"✅ Encontrados {len(input_devices)} dispositivo(s) de entrada:")
            for i, device in enumerate(input_devices):
                print(f"   {i}: {device['name']}")
        else:
            print("❌ Nenhum dispositivo de entrada encontrado")
            return False
            
        # Testar dispositivo padrão
        default_device = sd.default.device[0]
        if default_device is not None:
            print(f"✅ Dispositivo padrão: {devices[default_device]['name']}")
        else:
            print("⚠️  Nenhum dispositivo padrão configurado")
            
    except Exception as e:
        print(f"❌ Erro ao testar dispositivos de áudio: {e}")
        return False
    
    return True

def test_porcupine_key():
    """Testa se a chave do Porcupine está configurada"""
    print("\n🔑 Testando configuração do Porcupine...")
    print("=" * 40)
    
    access_key = os.getenv('PORCUPINE_ACCESS_KEY')
    
    if access_key:
        print("✅ Chave do Porcupine configurada")
        try:
            import pvporcupine
            porcupine = pvporcupine.create(access_key=access_key, keywords=['jarvis'])
            print("✅ Porcupine inicializado com sucesso!")
            porcupine.delete()
        except Exception as e:
            print(f"❌ Erro ao inicializar Porcupine: {e}")
            return False
    else:
        print("⚠️  Chave do Porcupine não configurada")
        print("💡 Configure: export PORCUPINE_ACCESS_KEY='sua_chave'")
        return False
    
    return True

def test_vosk_model():
    """Testa se há um modelo Vosk disponível"""
    print("\n🗣️  Testando modelo Vosk...")
    print("=" * 40)
    
    possible_paths = [
        "/usr/share/vosk-models",
        "/usr/local/share/vosk-models",
        os.path.expanduser("~/vosk-models"),
        "./vosk-models"
    ]
    
    model_found = False
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            print(f"📁 Verificando: {base_path}")
            for model_dir in os.listdir(base_path):
                model_path = os.path.join(base_path, model_dir)
                if os.path.isdir(model_path):
                    print(f"✅ Modelo encontrado: {model_path}")
                    model_found = True
                    break
            if model_found:
                break
    
    if not model_found:
        print("⚠️  Nenhum modelo Vosk encontrado")
        print("💡 Baixe um modelo em: https://alphacephei.com/vosk/models/")
        return False
    
    return True

def main():
    """Função principal de teste"""
    print("🤖 Jarvis - Teste de Instalação")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_audio_devices,
        test_porcupine_key,
        test_vosk_model
    ]
    
    passed_tests = 0
    
    for test in tests:
        if test():
            passed_tests += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultado: {passed_tests}/{len(tests)} testes passaram")
    
    if passed_tests == len(tests):
        print("🎉 Jarvis está completamente configurado!")
        print("🚀 Execute: python3 jarvis_assistant.py")
    else:
        print("⚠️  Alguns testes falharam. Verifique as mensagens acima.")
        print("📖 Consulte o README.md para instruções detalhadas.")
    
    return passed_tests == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
