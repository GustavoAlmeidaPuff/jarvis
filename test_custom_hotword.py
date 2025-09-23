#!/usr/bin/env python3
"""
Teste específico para verificar se a hotword personalizada está funcionando
"""

import os
import sys

def test_custom_hotword():
    """Testa se a hotword personalizada está disponível"""
    print("🔑 Testando hotword personalizada...")
    print("=" * 40)
    
    # Verificar se o arquivo existe
    custom_keyword_path = os.path.join(os.getcwd(), 'jarvis_custom.ppn')
    
    if os.path.exists(custom_keyword_path):
        print(f"✅ Arquivo de hotword personalizada encontrado: {custom_keyword_path}")
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(custom_keyword_path)
        print(f"📁 Tamanho do arquivo: {file_size} bytes")
        
        # Tentar inicializar Porcupine com hotword personalizada
        try:
            import pvporcupine
            
            # Verificar se há chave de acesso
            access_key = os.getenv('PORCUPINE_ACCESS_KEY')
            
            if not access_key:
                print("⚠️  Chave de acesso do Porcupine não configurada")
                print("💡 Configure: export PORCUPINE_ACCESS_KEY='sua_chave'")
                return False
            
            print("🧪 Testando inicialização do Porcupine...")
            porcupine = pvporcupine.create(
                access_key=access_key,
                keyword_paths=[custom_keyword_path]
            )
            
            print("✅ Porcupine inicializado com sucesso com hotword personalizada!")
            print("🎤 Sua hotword personalizada 'jarvis' está pronta para uso!")
            
            # Limpar recursos
            porcupine.delete()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar Porcupine com hotword personalizada: {e}")
            return False
    else:
        print(f"❌ Arquivo de hotword personalizada não encontrado: {custom_keyword_path}")
        print("💡 Certifique-se de que o arquivo jarvis_custom.ppn está no diretório do projeto")
        return False

def test_fallback_hotword():
    """Testa hotword padrão como fallback"""
    print("\n🔄 Testando hotword padrão como fallback...")
    print("=" * 40)
    
    try:
        import pvporcupine
        
        # Verificar se há chave de acesso
        access_key = os.getenv('PORCUPINE_ACCESS_KEY')
        
        if access_key:
            print("✅ Chave do Porcupine configurada")
            porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=['jarvis']
            )
            print("✅ Porcupine inicializado com hotword padrão!")
            porcupine.delete()
            return True
        else:
            print("⚠️  Chave do Porcupine não configurada")
            print("💡 Configure: export PORCUPINE_ACCESS_KEY='sua_chave'")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar hotword padrão: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🤖 Jarvis - Teste de Hotword Personalizada")
    print("=" * 50)
    
    # Testar hotword personalizada
    custom_works = test_custom_hotword()
    
    # Testar fallback
    fallback_works = test_fallback_hotword()
    
    print("\n" + "=" * 50)
    print("📊 Resultado dos Testes:")
    print(f"   - Hotword personalizada: {'✅' if custom_works else '❌'}")
    print(f"   - Hotword padrão (fallback): {'✅' if fallback_works else '❌'}")
    
    if custom_works:
        print("\n🎉 Sua hotword personalizada está funcionando!")
        print("🚀 Você pode executar o Jarvis sem precisar de chave de acesso!")
        print("💡 Execute: python3 jarvis_assistant.py")
    elif fallback_works:
        print("\n⚠️  Hotword personalizada não funcionou, mas o fallback está OK")
        print("💡 Configure sua chave do Porcupine para usar hotword padrão")
    else:
        print("\n❌ Nenhuma hotword está funcionando")
        print("💡 Verifique a instalação do Porcupine e configurações")
    
    return custom_works or fallback_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
