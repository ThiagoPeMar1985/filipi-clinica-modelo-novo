"""
Inicialização do módulo de atendimento
"""

# Importa os submódulos para disponibilizá-los quando o pacote for importado
try:
    from .agendamento_module import AgendamentoModule, MedicoCalendar
except ImportError:
    # Tratamento para quando o tkcalendar não estiver disponível
    print("Aviso: Módulo tkcalendar não encontrado. Funcionalidades de agendamento podem estar limitadas.")