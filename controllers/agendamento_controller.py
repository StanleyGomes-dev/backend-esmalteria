from datetime import datetime

def calcular_horarios_disponiveis(data_str):
    """
    Recebe uma data (string), aplica as regras de negócio e retorna os horários.
    Não sabe o que é Flask, nem Internet. É pura lógica.
    """
    if not data_str:
        return {"erro": "Data não informada"}

    try:
        # 1. Converter String para Objeto
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        dia_semana = data_obj.weekday() # 0=Segunda ... 6=Domingo
        
        # 2. A Regra da Irmã (Encapsulada)
        if dia_semana < 5: # Segunda a Sexta
            return {
                "mensagem": "Dia Útil (Faculdade)",
                "horarios": ["09:00", "19:00"],
                "dia_semana_int": dia_semana
            }
        else: # Sábado e Domingo
            return {
                "mensagem": "Fim de Semana (Livre)",
                "horarios": ["09:00", "14:00", "16:30", "19:00"],
                "dia_semana_int": dia_semana
            }
            
    except ValueError:
        return {"erro": "Formato de data inválido. Use AAAA-MM-DD"}