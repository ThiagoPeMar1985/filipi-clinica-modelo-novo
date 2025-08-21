import tkinter as tk
from tkinter import ttk

# Reaproveita toda a lógica e UI do módulo de Prontuário,
# apenas encapsulando com um cabeçalho/rotulagem de "Exames".
from .prontuario_module import ProntuarioModule

class ExamesProntuarioModule:
    """
    Módulo de Exames (Laudo) com o mesmo fluxo/layout do Prontuário.
    - Busca/seleção de paciente
    - Histórico de prontuários do paciente (estoque)
    - Editor de texto com inserção de modelo
    - Salvar prontuário (paciente_id, usuario_id, conteudo, data, titulo, consulta_id)

    Observação: Este wrapper mantém o mesmo comportamento de ProntuarioModule,
    mas rotula visualmente como "Exame/Laudo" para diferenciar de Consultas.
    Futuras diferenças (imagens, etc.) podem ser adicionadas aqui sem impactar consultas.
    """

    def __init__(self, parent, controller, db_connection=None):
        self.parent = parent
        self.controller = controller
        self.db_connection = db_connection

        # Frame raiz do módulo de Exames
        self.frame = ttk.Frame(parent)

        # Cabeçalho específico de Exames
        header = ttk.Label(self.frame, text="Laudo de Exame", font=("Segoe UI", 12, "bold"))
        header.pack(side=tk.TOP, anchor=tk.W, padx=8, pady=(8, 4))

        # Container para embutir o módulo de Prontuário original
        container = ttk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True)

        # Instancia o módulo de Prontuário (mesmo fluxo/layout e lógica)
        self.prontuario_module = ProntuarioModule(container, controller, db_connection=db_connection)

        # Importante: chama exibir() para construir toda a interface (busca paciente,
        # histórico, editor, inserir modelo, salvar, limpar), como em Consultas
        self.prontuario_module.exibir()

    # Repassa algumas propriedades úteis, se necessário
    @property
    def paciente_selecionado(self):
        return getattr(self.prontuario_module, 'paciente_selecionado', None)

    @property
    def usuario_dict(self):
        return getattr(self.prontuario_module, 'usuario_dict', None)

    # Exponha métodos conforme precisar no restante do app
    def get_frame(self):
        return self.frame

    def preselect_paciente_por_id(self, paciente_id):
        """Delegação para pré-selecionar paciente pelo ID no módulo interno."""
        try:
            if hasattr(self.prontuario_module, 'preselect_paciente_por_id'):
                self.prontuario_module.preselect_paciente_por_id(paciente_id)
        except Exception:
            pass
