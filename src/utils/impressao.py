"""
Módulo para gerenciamento de impressão de cupons e relatórios.
"""
import win32print
import win32ui
import win32con
import win32api
import win32gui
import os
from pathlib import Path
import re

class GerenciadorImpressao:
    """Classe para gerenciar a impressão de cupons e relatórios."""
    
    def __init__(self, config_controller=None):
        """
        Inicializa o gerenciador de impressão.
        
        Args:
            config_controller: Controlador de configurações para obter as impressoras configuradas
        """
        self.config_controller = config_controller
        self.impressoras = {}
        # Modo de impressão: 'a4' (padrão) ou 'termica'
        self.modo_impressao = 'a4'
        self._carregar_configuracoes()
        
        # Inicializa o mapeamento de tipos vazio - será carregado do banco
        self.mapeamento_tipos = {}
        self._carregar_mapeamento_banco()  

        # Tenta carregar o modo de impressão do config, se existir
        try:
            if hasattr(self.config_controller, 'carregar_config_impressoras'):
                _cfg = self.config_controller.carregar_config_impressoras() or {}
                modo = str(_cfg.get('modo_impressao', '')).strip().lower()
                if modo in ('a4', 'termica'):
                    self.modo_impressao = modo
        except Exception:
            pass
        
    def _carregar_mapeamento_banco(self):
        """
        Carrega o mapeamento de tipos de produtos para impressoras do banco de dados.
        
        Returns:
            bool: True se o carregamento foi bem-sucedido, False caso contrário
        """
        conn = None
        cursor = None
        try:
            import mysql.connector
            from mysql.connector import errors as _mysql_errors
            from src.db.config import get_db_config

            db_config = get_db_config()
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Verifica se as tabelas necessárias existem antes de consultar
            cursor.execute(
                """
                SELECT COUNT(*) AS qtd
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                  AND table_name IN ('impressoras_tipos', 'tipos_produtos')
                """
            )
            qtd = (cursor.fetchone() or {}).get('qtd', 0)
            if int(qtd) < 2:
                # Tabelas não existem no banco atual: segue sem mapeamento
                return False

            # Busca todos os mapeamentos de tipos para impressoras
            cursor.execute(
                """
                SELECT tp.nome as tipo, it.impressora_id 
                FROM impressoras_tipos it
                JOIN tipos_produtos tp ON it.tipo_id = tp.id
                """
            )

            resultados = cursor.fetchall() or []
            if resultados:
                self.mapeamento_tipos = {item['tipo']: str(item['impressora_id']) for item in resultados}
                return True
            # Sem registros: considera sem mapeamento, mas sem erro
            return False
        except Exception as e:
            # Trata especificamente tabela inexistente (1146) sem stack trace
            try:
                if hasattr(e, 'errno') and int(getattr(e, 'errno')) == 1146:
                    return False
            except Exception:
                pass
            # Outros erros: log leve e segue sem mapeamento
            print(f"[ERRO] Falha ao carregar mapeamento do banco: {e}")
            return False
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
    
    def _carregar_configuracoes(self):
        """Carrega as configurações de impressoras do sistema."""
        # Inicializa dicionário vazio de impressoras
        self.impressoras = {
            'impressora 1': '',  # Padrão para cupom fiscal
            'impressora 2': '',
            'impressora 3': '',
            'impressora 4': '',
            'impressora 5': '',
            'impressora 6': ''
        }
        
        # Verifica se temos um config_controller válido
        if not self.config_controller:
            # Nenhum config_controller fornecido ao GerenciadorImpressao
            pass
        else:
            # Verifica se o config_controller tem o método necessário
            if hasattr(self.config_controller, 'carregar_config_impressoras'):
                try:
                    config = self.config_controller.carregar_config_impressoras()
                    
                    if config and isinstance(config, dict):
                        # Mapeia as configurações para as chaves corretas
                        for i in range(1, 7):
                            chave = f'impressora {i}'
                            if chave in config and config[chave]:
                                self.impressoras[chave] = config[chave]
                        
                        return
                    
                except Exception as e:
                    print(f"[ERRO] Erro ao carregar configurações de impressão: {e}")
        
        # Se chegou aqui, não conseguiu carregar as configurações do config_controller
        # Tenta obter a impressora padrão do sistema
        try:
            impressora_padrao = win32print.GetDefaultPrinter()
            
            # Define a impressora padrão para todos os tipos
            for chave in self.impressoras:
                self.impressoras[chave] = impressora_padrao
            
        except Exception as e:
            # Mantém o dicionário vazio em caso de erro
            self.impressoras = {}
        
        
    # =========================
    # Impressão A4 (GDI) - Base
    # =========================
    def _imprimir_texto_a4(self, impressora: str, texto: str) -> bool:
        """Imprime texto em impressoras A4 com layout legível (fonte proporcional, margens).
        Faz uma quebra simples de linha por palavras para não extrapolar a largura da página.
        """
        if not impressora or not texto:
            return False

        hdc = None
        try:
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(impressora)
            hdc.StartDoc('Impressão A4')
            hdc.StartPage()

            # Fonte proporcional para documentos A4 com tamanho configurável (padrão 10, permitido 6-12)
            tamanho_pt = 10
            try:
                if self.config_controller and hasattr(self.config_controller, 'carregar_config_impressoras'):
                    _cfg = self.config_controller.carregar_config_impressoras() or {}
                    pt = int(_cfg.get('fonte_tamanho_a4', tamanho_pt))
                    if 6 <= pt <= 12:
                        tamanho_pt = pt
            except Exception:
                pass
            # DPI será obtido abaixo; inicializamos com fallback e corrigimos após medir DPI
            altura_fonte = -int(tamanho_pt * 96 / 72)
            font = win32ui.CreateFont({'name': 'Times New Roman', 'height': altura_fonte, 'weight': 400})
            hdc.SelectObject(font)

            # Margens físicas em milímetros, convertidas por DPI da impressora (padrão: 10mm)
            try:
                dpi_x = hdc.GetDeviceCaps(win32con.LOGPIXELSX)
                dpi_y = hdc.GetDeviceCaps(win32con.LOGPIXELSY)
            except Exception:
                dpi_x = 300
                dpi_y = 300
            # Ajusta fonte agora com DPI real (altura em unidades lógicas = -pt * dpi / 72)
            try:
                altura_fonte = -int(tamanho_pt * dpi_y / 72)
                font = win32ui.CreateFont({'name': 'Times New Roman', 'height': altura_fonte, 'weight': 400})
                hdc.SelectObject(font)
            except Exception:
                pass
            MARGEM_MM = 10  # ~1 cm solicitado
            def mm_to_px(mm, dpi):
                return int((mm / 25.4) * dpi)
            margem_esq = mm_to_px(MARGEM_MM, dpi_x)
            margem_dir = mm_to_px(MARGEM_MM, dpi_x)
            margem_top = mm_to_px(MARGEM_MM, dpi_y)
            margem_bot = mm_to_px(MARGEM_MM, dpi_y)

            # Tamanho da página em unidades do dispositivo
            horz_res = hdc.GetDeviceCaps(win32con.HORZRES)
            vert_res = hdc.GetDeviceCaps(win32con.VERTRES)
            largura_util = max(0, horz_res - margem_esq - margem_dir)
            altura_util = max(0, vert_res - margem_top - margem_bot)

            # Altura de linha aproximada
            tm = hdc.GetTextMetrics()
            linha_h = tm["tmHeight"] + tm["tmExternalLeading"]
            y = margem_top

            # Diretriz opcional "<<font:N>>" para ajustar tamanho (6..12)
            # Agora detectamos na PRIMEIRA OCORRÊNCIA em QUALQUER linha e removemos essa linha
            try:
                _lines = texto.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                idx_decl = -1
                decl_val = None
                for i, ln in enumerate(_lines):
                    s = ln.strip()
                    if s.lower().startswith('<<font:') and s.endswith('>>'):
                        try:
                            v = int(s[7:-2])
                            if 6 <= v <= 12:
                                idx_decl = i
                                decl_val = v
                                break
                        except Exception:
                            continue
                if idx_decl >= 0 and decl_val is not None:
                    tamanho_pt = decl_val
                    # Atualiza fonte usando DPI real
                    try:
                        altura_fonte = -int(tamanho_pt * dpi_y / 72)
                        font = win32ui.CreateFont({'name': 'Times New Roman', 'height': altura_fonte, 'weight': 400})
                        hdc.SelectObject(font)
                        # Recalcula métricas para a nova fonte
                        tm_local = hdc.GetTextMetrics()
                        linha_h = tm_local["tmHeight"] + tm_local["tmExternalLeading"]
                    except Exception:
                        pass
                    # Remove a linha da diretiva do conteúdo a imprimir
                    del _lines[idx_decl]
                    texto = '\n'.join(_lines)
            except Exception:
                pass

            # Word-wrap por palavras, respeitando largura útil e paginando
            # Suporta alinhamento por linha via tags iniciais: <<center>> e <<right>>
            # align_hint: 'left' | 'center' | 'right' sugerido externamente (ex.: heurística do CRM)
            def draw_wrapped(paragraph: str, align_hint: str = 'left'):
                nonlocal y
                if paragraph == "":
                    # Linha em branco
                    if y > (margem_top + altura_util - linha_h):
                        hdc.EndPage(); hdc.StartPage(); hdc.SelectObject(font); y = margem_top
                    hdc.TextOut(margem_esq, y, "")
                    y += linha_h
                    return
                # Detecta tag de alinhamento no início da linha
                align = align_hint or 'left'
                s_strip = paragraph.strip()
                lowered = s_strip.lower()
                if lowered.startswith('<<center>>'):
                    paragraph = paragraph.lower().replace('<<center>>', '', 1).lstrip()
                    align = 'center'
                elif lowered.startswith('<<right>>'):
                    paragraph = paragraph.lower().replace('<<right>>', '', 1).lstrip()
                    align = 'right'

                words = paragraph.split()
                linha_atual = ""
                for w in words:
                    tentativa = (linha_atual + (" " if linha_atual else "") + w)
                    try:
                        largura = hdc.GetTextExtent(tentativa)[0]
                    except Exception:
                        largura = 0
                    if largura <= largura_util:
                        linha_atual = tentativa
                    else:
                        # Desenha linha_atual e quebra
                        if y > (margem_top + altura_util - linha_h):
                            hdc.EndPage(); hdc.StartPage(); hdc.SelectObject(font); y = margem_top
                        # Calcula x conforme alinhamento
                        try:
                            w_px = hdc.GetTextExtent(linha_atual)[0]
                        except Exception:
                            w_px = 0
                        if align == 'center':
                            x = margem_esq + max(0, (largura_util - w_px)//2)
                        elif align == 'right':
                            x = margem_esq + max(0, largura_util - w_px)
                        else:
                            x = margem_esq
                        hdc.TextOut(x, y, linha_atual)
                        y += linha_h
                        linha_atual = w
                # desenha resto
                if linha_atual or paragraph.endswith(" "):
                    if y > (margem_top + altura_util - linha_h):
                        hdc.EndPage(); hdc.StartPage(); hdc.SelectObject(font); y = margem_top
                    try:
                        w_px = hdc.GetTextExtent(linha_atual)[0]
                    except Exception:
                        w_px = 0
                    if align == 'center':
                        x = margem_esq + max(0, (largura_util - w_px)//2)
                    elif align == 'right':
                        x = margem_esq + max(0, largura_util - w_px)
                    else:
                        x = margem_esq
                    hdc.TextOut(x, y, linha_atual)
                    y += linha_h

            linhas_full = texto.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            # Heurística: se a linha contiver 'crm', ALINHA AO CENTRO e
            # centraliza a linha imediatamente anterior (nome do médico).
            # Adiciona 5 linhas de espaçamento APENAS antes da linha do nome (primeira do bloco)
            indices_center = set()
            indices_first_of_block = set()
            for i, ln in enumerate(linhas_full):
                if 'crm' in ln.lower():
                    indices_center.add(i)
                    if i > 0:
                        indices_center.add(i-1)
                        indices_first_of_block.add(i-1)

            # Versão com espaçamento extra antes do bloco Nome/CRM
            def draw_with_spacing(i: int, par: str):
                nonlocal y
                if i in indices_first_of_block:
                    # adiciona 5 linhas DEPOIS do texto anterior, antes do nome
                    y += 5 * linha_h
                draw_wrapped(par, 'center' if i in indices_center else 'left')

            for i, par in enumerate(linhas_full):
                draw_with_spacing(i, par)

            hdc.EndPage()
            hdc.EndDoc()
            return True
        except Exception as e:
            print(f"ERRO na impressão A4: {e}")
            return False
        finally:
            try:
                if hdc is not None:
                    pass
            except Exception:
                pass

    

    # ==============================
    # 1) Comprovante de Pagamento
    # ==============================
    def imprimir_comprovante_pagamento(self,
                                       empresa: dict,
                                       paciente: dict,
                                       pagamentos: list,
                                       itens: list | None = None,
                                       impressora: str | None = None) -> bool:
        """
        Imprime um comprovante de pagamento A4.

        empresa: {nome_fantasia, cnpj, ...}
        paciente: {nome, documento, nasc, ...}
        pagamentos: lista de {forma, valor}
        itens: opcional lista de {descricao, qtd, valor}
        """
        # Sem QUALQUER formatação: imprime apenas linhas simples derivadas das entradas
        linhas = []
        if itens:
            for it in itens:
                try:
                    linhas.append(str(it))
                except Exception:
                    pass
        if pagamentos:
            for p in pagamentos:
                try:
                    linhas.append(str(p))
                except Exception:
                    pass
        texto = '\n'.join(linhas)
        alvo = impressora or self.impressoras.get('impressora 1') or win32print.GetDefaultPrinter()
        return self._imprimir_texto_a4(alvo, texto)

    # ======================
    # 2) Laudo Médico (A4)
    # ======================
    def imprimir_laudo_medico(self,
                               empresa: dict,
                               paciente: dict,
                               medico: dict,
                               laudo: dict,
                               impressora: str | None = None) -> bool:
        """
        Imprime Laudo Médico padronizado A4.

        paciente: {nome, documento, nasc}
        medico: {nome, crm}
        laudo: {titulo, corpo, data, assinatura_texto}
        """
        # Impressão SEM QUALQUER formatação adicional: usa somente o corpo já gerado
        texto = str((laudo or {}).get('corpo') or '')
        alvo = impressora or self.impressoras.get('impressora 2') or self.impressoras.get('impressora 1') or win32print.GetDefaultPrinter()
        return self._imprimir_texto_a4(alvo, texto)

    # ======================
    # 3) Receituário (A4)
    # ======================
    def imprimir_receita_texto(self, texto: str, impressora: str | None = None) -> bool:
        """Imprime uma RECEITA A4 a partir de um TEXTO já pronto.
        Nenhuma formatação extra é adicionada aqui. A função apenas encaminha o texto
        para a impressora alvo, honrando a diretiva inicial <<font:N>> caso exista.
        """
        try:
            alvo = impressora or self.impressoras.get('impressora 2') or self.impressoras.get('impressora 1') or win32print.GetDefaultPrinter()
        except Exception:
            alvo = impressora
        return self._imprimir_texto_a4(alvo, texto)
    def imprimir_receituario(self,
                             empresa: dict,
                             paciente: dict,
                             medico: dict,
                             prescricoes: list,
                             observacoes: str | None = None,
                             impressora: str | None = None) -> bool:
        """
        Imprime Receituário A4.

        prescricoes: lista de strings ou de dicts; sem formatação.
        """
        # Sem QUALQUER formatação: usa texto pronto se string; caso lista, apenas junta os itens
        if isinstance(prescricoes, str):
            texto = prescricoes
        else:
            linhas = []
            for p in (prescricoes or []):
                try:
                    if isinstance(p, dict):
                        # Concatena valores existentes numa linha simples
                        valores = [str(v) for v in p.values() if v]
                        linhas.append(' '.join(valores))
                    else:
                        linhas.append(str(p))
                except Exception:
                    pass
            texto = '\n'.join(linhas)
        if observacoes:
            texto = (texto + ('\n' if texto else '')) + str(observacoes)
        alvo = impressora or self.impressoras.get('impressora 3') or self.impressoras.get('impressora 1') or win32print.GetDefaultPrinter()
        return self._imprimir_texto_a4(alvo, texto)