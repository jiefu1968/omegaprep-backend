import re

def formatar_texto_ia(texto: str) -> str:
    """
    Remove marcações desnecessárias da IA e formata símbolos matemáticos
    para uma melhor visualização no frontend.
    """
    if not texto:
        return ""

    # 1. Remove marcações de bloco de código markdown, se existirem
    texto = texto.replace("```json", "").replace("```", "")
    
    # 2. Substitui potências comuns para formato de sobrescrito (superscript)
    # Usamos replace direto para garantir que o símbolo '^' não seja interpretado como Regex
    texto = texto.replace("^2", "²")
    texto = texto.replace("^3", "³")
    
    # 3. Limpezas adicionais de espaçamento
    texto = texto.strip()
    
    return texto