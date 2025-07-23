import tkinter as tk
from tkinter import messagebox
import datetime

class ModoEdicaoMesas:
    def __init__(self, parent):
        self.parent = parent
        self._em_modo_edicao = False
        self.barra_lateral_sobreposicao = None
        self.barra_superior_sobreposicao = None
        
    def limpar_itens_sessao(self):
        """
        Limpa a lista de itens adicionados na sessão atual
        """
        try:
            # Limpar a lista de itens no controlador de mesas, se existir
            if hasattr(self.parent, 'controller_mesas'):
                if hasattr(self.parent.controller_mesas, 'limpar_itens_sessao'):
                    self.parent.controller_mesas.limpar_itens_sessao()
                elif hasattr(self.parent.controller_mesas, 'itens_adicionados_na_sessao'):
                    self.parent.controller_mesas.itens_adicionados_na_sessao = []
            
            # Limpar a lista local no módulo principal, se existir
            if hasattr(self.parent, 'itens_adicionados_na_sessao'):
                self.parent.itens_adicionados_na_sessao = []
                
            return True
            
        except Exception as e:
            print(f"Erro ao limpar itens da sessão: {e}")
            return False
            
    def adicionar_item_sessao(self, item):
        """
        Adiciona um item à lista de itens da sessão atual
        
        Args:
            item (dict): Dicionário contendo as informações do item a ser adicionado
        """
        try:
            # Verificar se o item é válido
            if not item or not isinstance(item, dict) or 'id' not in item:
                print("[ERRO] Item inválido para adicionar à sessão:", item)
                return False
                
            # Adicionar o item à lista no controlador de mesas, se existir
            if hasattr(self.parent, 'controller_mesas'):
                if hasattr(self.parent.controller_mesas, 'adicionar_item_sessao'):
                    return self.parent.controller_mesas.adicionar_item_sessao(item)
                elif hasattr(self.parent.controller_mesas, 'itens_adicionados_na_sessao'):
                    self.parent.controller_mesas.itens_adicionados_na_sessao.append(item)
            
            # Adicionar o item à lista local no módulo principal, se existir
            if hasattr(self.parent, 'itens_adicionados_na_sessao'):
                if not hasattr(self.parent, 'itens_adicionados_na_sessao'):
                    self.parent.itens_adicionados_na_sessao = []
                self.parent.itens_adicionados_na_sessao.append(item)
                
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar item à sessão: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _criar_barra_lateral_sobreposicao(self):
        """Cria a barra lateral de sobreposição"""
        if self.barra_lateral_sobreposicao is not None:
            return
            
        # Obter a janela principal
        janela_principal = self.parent.frame.winfo_toplevel()
        
        # Calcular a altura disponível (altura total - altura da barra superior)
        altura_disponivel = janela_principal.winfo_height() - 60  # Subtrai os 60px da barra superior
        
        # Criar um frame que cobre apenas a barra lateral
        # Usar cores padrão se não estiver definido
        cor_terciaria = self.parent.cores.get('terciaria', '#333f50') if hasattr(self.parent, 'cores') else '#333f50'
        
        self.barra_lateral_sobreposicao = tk.Frame(
            janela_principal,  # Usando a janela principal como pai
            bg=cor_terciaria,  # Usando a cor terciária do tema
            cursor='arrow',  # Cursor padrão para indicar que não é interativo
            width=200,  # Largura fixa para a barra lateral (igual ao sidebar principal)
            height=altura_disponivel  # Altura ajustada
        )
        
        # Posicionar o frame para cobrir a barra lateral, começando após a barra superior
        self.barra_lateral_sobreposicao.place(
            x=0, 
            y=60,  # Começa após a barra superior de 60px
            anchor='nw',
            height=altura_disponivel  # Usa a altura disponível
        )
        
        # Obter cores e fontes com valores padrão
        cor_terciaria = self.parent.cores.get('terciaria', '#333f50') if hasattr(self.parent, 'cores') else '#333f50'
        cor_texto = self.parent.cores.get('texto_claro', '#ffffff') if hasattr(self.parent, 'cores') else '#ffffff'
        fonte = self.parent.fontes.get('subtitulo', ('Arial', 12, 'bold')) if hasattr(self.parent, 'fontes') else ('Arial', 12, 'bold')
        
        # Adicionar texto informativo (opcional)
        label = tk.Label(
            self.barra_lateral_sobreposicao,
            text="Modo Edição Ativo",
            bg=cor_terciaria,
            fg=cor_texto,
            font=fonte,
            wraplength=150,
            justify='center'
        )
        label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Forçar o redesenho da janela
        self.barra_lateral_sobreposicao.update_idletasks()
        
        # Trazer para frente de todos os outros widgets
        self.barra_lateral_sobreposicao.lift()
        
        # Garantir que fique sempre visível
        self.barra_lateral_sobreposicao.tkraise()
    
    def _criar_barra_superior_sobreposicao(self):
        """Cria a barra superior de sobreposição"""
        if self.barra_superior_sobreposicao is not None:
            return
            
        # Obter a janela principal
        janela_principal = self.parent.frame.winfo_toplevel()
        
        # Obter cor primária com valor padrão
        cor_primaria = self.parent.cores.get('primaria', '#4a6fa5') if hasattr(self.parent, 'cores') else '#4a6fa5'
        
        # Criar um frame que cobre apenas a barra superior
        self.barra_superior_sobreposicao = tk.Frame(
            janela_principal,  # Usando a janela principal como pai
            bg=cor_primaria,  # Usando a cor primária (azul) da barra superior
            cursor='arrow',  # Cursor padrão para indicar que não é interativo
            height=60  # Altura fixa para a barra superior (60px - igual ao header principal)
        )
        
        # Posicionar o frame para cobrir a barra superior
        self.barra_superior_sobreposicao.place(
            x=0, 
            y=0, 
            relwidth=1.0,  # Largura total da janela
            anchor='nw'
        )
        
        # Obter cores e fontes com valores padrão
        cor_primaria = self.parent.cores.get('primaria', '#4a6fa5') if hasattr(self.parent, 'cores') else '#4a6fa5'
        cor_texto = self.parent.cores.get('texto_claro', '#ffffff') if hasattr(self.parent, 'cores') else '#ffffff'
        fonte = self.parent.fontes.get('subtitulo', ('Arial', 12, 'bold')) if hasattr(self.parent, 'fontes') else ('Arial', 12, 'bold')
        
        # Adicionar texto informativo (opcional)
        label = tk.Label(
            self.barra_superior_sobreposicao,
            text="MODO EDIÇÃO DE PEDIDO",
            bg=cor_primaria,
            fg=cor_texto,
            font=fonte,
            pady=15
        )
        label.pack(expand=True)
        
        # Forçar o redesenho da janela
        self.barra_superior_sobreposicao.update_idletasks()
        
        # Trazer para frente de todos os outros widgets
        self.barra_superior_sobreposicao.lift()
        
        # Garantir que fique sempre visível
        self.barra_superior_sobreposicao.tkraise()
    
    def _criar_barras_sobreposicao(self):
        """Cria as barras de sobreposição para o modo de edição"""
        self._criar_barra_lateral_sobreposicao()
        self._criar_barra_superior_sobreposicao()
    
    def _remover_barras_sobreposicao(self):
        """Remove todas as barras de sobreposição"""
        self._remover_barra_lateral_sobreposicao()
        self._remover_barra_superior_sobreposicao()
    
    def _remover_barra_lateral_sobreposicao(self):
        """Remove a barra lateral de sobreposição"""
        if hasattr(self, 'barra_lateral_sobreposicao') and self.barra_lateral_sobreposicao is not None:
            try:
                self.barra_lateral_sobreposicao.destroy()
            except:
                pass
            self.barra_lateral_sobreposicao = None
    
    def _remover_barra_superior_sobreposicao(self):
        """Remove a barra superior de sobreposição"""
        if hasattr(self, 'barra_superior_sobreposicao') and self.barra_superior_sobreposicao is not None:
            try:
                self.barra_superior_sobreposicao.destroy()
            except:
                pass
            self.barra_superior_sobreposicao = None
    
    def entrar_modo_edicao(self):
        """
        Método público para ativar o modo de edição
        Mantido para compatibilidade com código existente
        """
        self._entrar_modo_edicao()
    
    def _entrar_modo_edicao(self):
        """Ativa o modo de edição"""
        # Só executa se não estiver já em modo de edição
        if not hasattr(self, '_em_modo_edicao') or not self._em_modo_edicao:
            self._em_modo_edicao = True
            
            # Esconder botões padrão
            if hasattr(self.parent, 'botao_voltar'):
                self.parent.botao_voltar.pack_forget()
            if hasattr(self.parent, 'botao_finalizar'):
                self.parent.botao_finalizar.pack_forget()
            
            # Mostrar botões de edição
            if hasattr(self.parent, 'botao_cancelar'):
                self.parent.botao_cancelar.pack(side="left")
            if hasattr(self.parent, 'botao_confirmar'):
                # Usar os mesmos parâmetros de pack que o botão finalizar para manter o mesmo tamanho
                self.parent.botao_confirmar.pack(fill="x", pady=5, side="left", expand=True)
            
            # Adiciona as barras de sobreposição
            self._criar_barras_sobreposicao()
            
            # Atualizar a interface
            if hasattr(self.parent, 'update'):
                self.parent.update()
    
    def _sair_modo_edicao(self, confirmar=False):
        """
        Desativa o modo de edição, mostrando os botões originais
        
        Args:
            confirmar: Se True, mantém as alterações. Se False, descarta as alterações.
        """
        if hasattr(self, '_em_modo_edicao') and self._em_modo_edicao:
            self._em_modo_edicao = False
            
            # Esconder botões de edição
            if hasattr(self.parent, 'botao_cancelar'):
                self.parent.botao_cancelar.pack_forget()
            if hasattr(self.parent, 'botao_confirmar'):
                self.parent.botao_confirmar.pack_forget()
            
            # Mostrar botões padrão
            if hasattr(self.parent, 'botao_voltar'):
                self.parent.botao_voltar.pack(side="left")
            if hasattr(self.parent, 'botao_finalizar'):
                self.parent.botao_finalizar.pack(fill="x", pady=5, side="left", expand=True)
            
            # Remove as barras de sobreposição
            self._remover_barras_sobreposicao()
            
            # Se for para confirmar as alterações, limpa a lista de itens da sessão
            if confirmar and hasattr(self.parent, 'itens_adicionados_na_sessao'):
                self.parent.itens_adicionados_na_sessao = []
                if hasattr(self.parent, 'itens_pedido'):
                    if not hasattr(self.parent, 'itens_originais'):
                        self.parent.itens_originais = []
                    self.parent.itens_originais = self.parent.itens_pedido.copy()
            
            # Atualizar a interface
            if hasattr(self.parent, 'update'):
                self.parent.update()
    
    def cancelar_alteracoes(self):
        """Cancela as alterações e volta para o estado anterior"""
        try:
            # Verificar se o controlador de mesas está disponível
            if not hasattr(self.parent, 'controller_mesas') or not hasattr(self.parent.controller_mesas, 'itens_adicionados_na_sessao'):
                messagebox.showerror("Erro", "Não foi possível acessar os itens da sessão.")
                self._sair_modo_edicao()
                return
                
            # Obter a lista de itens adicionados na sessão do controlador
            itens_para_remover = self.parent.controller_mesas.itens_adicionados_na_sessao
            
            if not itens_para_remover:
                # Se não houver itens adicionados na sessão, apenas sai do modo de edição
                self._sair_modo_edicao()
                return
                
            # Obter detalhes dos itens a serem removidos
            itens_detalhes = []
            if hasattr(self.parent, 'tabela_itens'):
                for item in itens_para_remover:
                    if 'id' in item:
                        # Buscar detalhes do item na tabela de itens
                        for child in self.parent.tabela_itens.get_children():
                            valores = self.parent.tabela_itens.item(child, 'values')
                            if valores and len(valores) > 1 and str(valores[0]) == str(item['id']):
                                nome_item = valores[1] if len(valores) > 1 else f"Item {item['id']}"
                                quantidade = valores[2] if len(valores) > 2 else "1"
                                itens_detalhes.append(f"- {quantidade}x {nome_item}")
                                break
            
            # Criar mensagem com detalhes dos itens
            mensagem = "Tem certeza que deseja cancelar as alterações?\n\n"
            mensagem += f"Os seguintes {len(itens_para_remover)} itens serão removidos:\n"
            
            # Adicionar detalhes dos itens à mensagem
            if itens_detalhes:
                mensagem += "\n".join(itens_detalhes[:10])  # Limita a 10 itens para não ficar muito grande
                if len(itens_detalhes) > 10:
                    mensagem += f"\n...e mais {len(itens_detalhes) - 10} itens"
            else:
                mensagem += f"- {len(itens_para_remover)} itens sem detalhes disponíveis"
            
            # Perguntar confirmação
            if not messagebox.askyesno(
                "Cancelar Alterações",
                mensagem
            ):
                return
                
            # Verificar se há um pedido atual
            if not hasattr(self.parent, 'pedido_atual') or not self.parent.pedido_atual or 'id' not in self.parent.pedido_atual:
                messagebox.showerror("Erro", "Nenhum pedido em andamento.")
                self._sair_modo_edicao()
                return
                
            # Remover itens adicionados na sessão
            itens_removidos = 0
            erros = []
            
            # Para cada item adicionado na sessão, removê-lo do pedido
            for item in itens_para_remover:
                if 'id' in item:
                    try:
                        # Remover o item do banco de dados
                        sucesso, mensagem = self.parent.controller_mesas.remover_item_pedido(item_id=item['id'])
                        if sucesso:
                            itens_removidos += 1
                        else:
                            erros.append(f"Falha ao remover item {item['id']}: {mensagem}")
                    except Exception as e:
                        erro_msg = f"Erro ao remover item {item['id']}: {str(e)}"
                        erros.append(erro_msg)
            
            # Limpar a lista de itens adicionados na sessão no controlador
            if hasattr(self.parent.controller_mesas, 'limpar_itens_sessao'):
                self.parent.controller_mesas.limpar_itens_sessao()
            
            # Recarregar os itens do pedido do banco de dados
            if hasattr(self.parent, 'carregar_pedidos'):
                self.parent.carregar_pedidos(manter_itens_sessao=False)
            
            # Atualizar a interface
            if hasattr(self.parent, 'atualizar_interface'):
                self.parent.atualizar_interface()
            
            # Sair do modo de edição
            self._sair_modo_edicao(confirmar=False)
            
            # Mostrar mensagem apenas em caso de erro
            if erros:
                messagebox.showwarning(
                    "Aviso", 
                    f"{itens_removidos} itens removidos com sucesso.\n"
                    f"{len(erros)} itens não puderam ser removidos.\n\n"
                    f"Erros encontrados:\n" + "\n".join(erros[:5])
                )
            
            # Voltar para a tela de visualizar mesas, se disponível
            if hasattr(self.parent, 'voltar_para_mesas'):
                self.parent.voltar_para_mesas()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao cancelar alterações: {str(e)}")
    
    def confirmar_alteracoes(self):
        """Confirma as alterações e volta para o estado normal e imprime apenas os itens adicionados na sessão"""
        try:
            # Verificar se o controlador de mesas está disponível
            if not hasattr(self.parent, 'controller_mesas') or not hasattr(self.parent.controller_mesas, 'itens_adicionados_na_sessao'):
                messagebox.showerror("Erro", "Não foi possível acessar os itens da sessão.")
                return
                
            # Verificar se há itens adicionados na sessão para imprimir
            itens_sessao = self.parent.controller_mesas.itens_adicionados_na_sessao
            if not itens_sessao:
                messagebox.showinfo("Aviso", "Não há novos itens para imprimir.")
                self._sair_modo_edicao(confirmar=True)
                return
                
            # Verificar se há um pedido atual
            if not hasattr(self.parent, 'pedido_atual') or not self.parent.pedido_atual:
                messagebox.showerror("Erro", "Não há pedido atual para confirmar alterações.")
                return
                
            # Verificar se há uma mesa definida
            if not hasattr(self.parent, 'mesa') or not self.parent.mesa or 'numero' not in self.parent.mesa:
                messagebox.showerror("Erro", "Nenhuma mesa selecionada.")
                return
            
            # Inicializar o gerenciador de impressão
            try:
                from controllers.config_controller import ConfigController
                from utils.impressao import GerenciadorImpressao
                
                config_controller = ConfigController()
                gerenciador_impressao = GerenciadorImpressao(config_controller=config_controller)
            except ImportError as e:
                messagebox.showerror("Erro", f"Falha ao importar módulos necessários: {str(e)}")
                return
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao inicializar o gerenciador de impressão: {str(e)}")
                return
            
            # Lista para armazenar os itens que serão impressos
            itens_para_imprimir = []
            
            # Verificar se temos conexão com o banco de dados
            if not hasattr(self.parent, 'db_connection') or not self.parent.db_connection:
                messagebox.showerror("Erro", "Sem conexão com o banco de dados.")
                return
            
            # Buscar os detalhes completos dos itens adicionados na sessão
            try:
               
                
                # Primeiro, filtrar apenas itens completos (com 'id' e 'produto_id')
                itens_completos = [item for item in itens_sessao 
                                 if isinstance(item, dict) and 'id' in item and 'produto_id' in item]
                
                # Usar todos os itens sem verificação de duplicados
                itens_sessao = itens_completos
                
                cursor = self.parent.db_connection.cursor(dictionary=True)
                
                for item_sessao in itens_sessao:
                    
                    if 'id' in item_sessao and item_sessao['id']:
                        # Buscar o item completo no banco de dados
                        cursor.execute("""
                            SELECT ip.*, p.nome as nome_produto, p.tipo 
                            FROM itens_pedido ip
                            JOIN produtos p ON ip.produto_id = p.id
                            WHERE ip.id = %s
                        """, (item_sessao['id'],))
                            
                        item_completo = cursor.fetchone()
                        
                        if item_completo:
                            # Buscar as opções do item, se houver
                            cursor.execute("""
                                SELECT * FROM itens_pedido_opcoes 
                                WHERE item_pedido_id = %s
                            """, (item_sessao['id'],))
                            
                            opcoes = cursor.fetchall()
                            item_completo['opcoes'] = opcoes
                            
                           
                            
                            # Renomear o campo valor_unitario para preco_unitario se necessário
                            if 'valor_unitario' in item_completo and ('preco_unitario' not in item_completo or item_completo['preco_unitario'] is None):
                                item_completo['preco_unitario'] = item_completo['valor_unitario']
                            
                            # Garantir que todos os campos necessários existam
                            campos_necessarios = {
                                'nome': item_completo.get('nome_produto', 'Produto sem nome'),
                                'quantidade': item_completo.get('quantidade', 1),
                                'tipo': item_completo.get('tipo', 'Outros')
                            }
                            
                            # Adicionar os campos necessários ao item
                            for campo, valor in campos_necessarios.items():
                                if campo not in item_completo or item_completo[campo] is None:
                                    item_completo[campo] = valor
                            
                            itens_para_imprimir.append(item_completo)
                        
                cursor.close()
                
            except Exception as e:
                if 'cursor' in locals():
                    cursor.close()
                messagebox.showerror("Erro", f"Erro ao buscar itens do pedido: {str(e)}")
                return
            
            # Se encontrou itens para imprimir
            if itens_para_imprimir:
                # Buscar o nome do usuário na tabela usuarios usando o usuario_id do pedido
                nome_usuario = 'Não identificado'
                usuario_id = self.parent.pedido_atual.get('usuario_id')
                
                if usuario_id:
                    try:
                        cursor = self.parent.db_connection.cursor(dictionary=True)
                        cursor.execute("SELECT nome FROM usuarios WHERE id = %s", (usuario_id,))
                        usuario = cursor.fetchone()
                        if usuario:
                            nome_usuario = usuario['nome']
                        cursor.close()
                    except Exception as e:
                        print(f"Erro ao buscar nome do usuário: {e}")
                
                # Informações do pedido para o cabeçalho da impressão
                info_pedido = {
                    'id': self.parent.pedido_atual['id'],
                    'mesa': self.parent.mesa['numero'],
                    'data_hora': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'tipo': 'ADICIONAL MESA',  # Indica que são itens adicionais
                    'tipo_venda': 'mesa',
                    'referencia': f"Mesa {self.parent.mesa['numero']} - Pedido #{self.parent.pedido_atual['id']} (Adicionais)",
                    'usuario_nome': nome_usuario  # Adiciona o nome do usuário
                }
                
                # Criar uma cópia dos itens para evitar modificar a lista original
                itens_para_impressao = []
                
                # Verificar e corrigir campos antes de enviar para impressão
                try:
                    for item in itens_para_imprimir:
                        # Criar uma cópia do item para evitar modificar o original
                        item_impressao = item.copy()
                        
                        # Garantir que o campo nome exista (necessário para impressão)
                        if 'nome' not in item_impressao:
                            item_impressao['nome'] = item_impressao.get('nome_produto', 'Produto sem nome')
                        
                        # Garantir que o campo produto_id exista
                        if 'produto_id' not in item_impressao and 'id_produto' in item_impressao:
                            item_impressao['produto_id'] = item_impressao['id_produto']
                        
                        itens_para_impressao.append(item_impressao)
                    
                    # Verificar se ainda há itens para imprimir
                    if itens_para_impressao:
                        gerenciador_impressao.imprimir_comandas_por_tipo(info_pedido, itens_para_impressao)
                        
                except Exception as e:
                    print(f"\nERRO durante a preparação para impressão: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Erro", f"Erro ao preparar itens para impressão: {str(e)}")
            
            # Limpar os itens da sessão no controlador
            if hasattr(self.parent.controller_mesas, 'limpar_itens_sessao'):
                self.parent.controller_mesas.limpar_itens_sessao()
            elif hasattr(self.parent.controller_mesas, 'itens_adicionados_na_sessao'):
                self.parent.controller_mesas.itens_adicionados_na_sessao = []
            
            # Sair do modo de edição e confirmar as alterações
            self._sair_modo_edicao(confirmar=True)
            
            # Recarregar os itens do pedido para garantir que tudo está sincronizado
            if hasattr(self.parent, 'carregar_pedidos'):
                self.parent.carregar_pedidos()
            
            # Atualizar a interface
            if hasattr(self.parent, 'atualizar_interface'):
                self.parent.atualizar_interface()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao confirmar alterações: {str(e)}")