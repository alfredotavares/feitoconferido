"""
Gerenciador de critérios JSON para o sistema Feito Conferido
"""

import json
import os
from typing import Dict, Any, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CriteriosManager:
    """Classe para gerenciar critérios de conformidade em formato JSON"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        self.project_root = Path(project_root)
        self.criterios_json_path = self.project_root / 'criterios.json'
        self.criterios_data = self._load_criterios_json()
    
    def _load_criterios_json(self) -> Dict[str, str]:
        """Carrega critérios do arquivo JSON"""
        try:
            if self.criterios_json_path.exists():
                with open(self.criterios_json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Arquivo criterios.json não encontrado em {self.criterios_json_path}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao carregar criterios.json: {e}")
            return {}
    
    def get_all_criterios(self) -> Dict[str, str]:
        """Retorna todos os critérios carregados"""
        return self.criterios_data.copy()
    
    def get_criterio(self, key: str) -> str:
        """Retorna um critério específico"""
        return self.criterios_data.get(key, "")
    
    def validate_data_against_criterios(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Valida dados contra os critérios JSON"""
        validation_results = []
        
        for criterio_key, criterio_desc in self.criterios_data.items():
            result = {
                'criterio': criterio_key,
                'descricao': criterio_desc,
                'status': 'NON-COMPLIANT',
                'justificativa': '',
                'valor_encontrado': None
            }
            
            # Verifica se o critério existe nos dados
            if criterio_key in data:
                valor = data[criterio_key]
                result['valor_encontrado'] = valor
                
                # Análise básica de conformidade
                if self._analyze_compliance(criterio_key, valor, criterio_desc):
                    result['status'] = 'COMPLIANT'
                    result['justificativa'] = f"Critério atendido: {valor}"
                else:
                    result['status'] = 'PARTIAL'
                    result['justificativa'] = f"Critério parcialmente atendido: {valor}"
            else:
                result['justificativa'] = f"Critério não encontrado nos dados"
            
            validation_results.append(result)
        
        return validation_results
    
    def _analyze_compliance(self, key: str, value: str, description: str) -> bool:
        """Analisa se um valor está em conformidade com o critério"""
        # Palavras-chave que indicam conformidade
        positive_keywords = [
            'implementado', 'entregue', 'configurado', 'aplicado', 
            'validado', 'ativo', 'operando', 'migrado', 'definidas',
            'criado', 'seguiram', 'atualizado'
        ]
        
        # Palavras-chave que indicam não conformidade
        negative_keywords = [
            'não', 'ainda não', 'sem', 'nenhum', 'faltando',
            'pendente', 'incompleto', 'falhou'
        ]
        
        value_lower = value.lower()
        
        # Verifica palavras negativas primeiro
        for neg_word in negative_keywords:
            if neg_word in value_lower:
                return False
        
        # Verifica palavras positivas
        for pos_word in positive_keywords:
            if pos_word in value_lower:
                return True
        
        # Se não encontrou indicadores claros, considera parcial
        return False
    
    def generate_compliance_report(self, data: Dict[str, Any]) -> str:
        """Gera relatório de conformidade em formato texto"""
        validation_results = self.validate_data_against_criterios(data)
        
        report_lines = [
            "RELATÓRIO DE CONFORMIDADE - CRITÉRIOS JSON",
            "=" * 50,
            ""
        ]
        
        compliant_count = 0
        partial_count = 0
        non_compliant_count = 0
        
        for result in validation_results:
            status = result['status']
            if status == 'COMPLIANT':
                compliant_count += 1
                status_symbol = "[CONFORME]"
            elif status == 'PARTIAL':
                partial_count += 1
                status_symbol = "[PARCIAL]"
            else:
                non_compliant_count += 1
                status_symbol = "[NÃO CONFORME]"
            
            report_lines.extend([
                f"{status_symbol} {result['criterio'].upper().replace('_', ' ')}:",
                f"   Descrição: {result['descricao']}",
                f"   Justificativa: {result['justificativa']}",
                ""
            ])
        
        # Resumo estatístico
        total = len(validation_results)
        report_lines.extend([
            "RESUMO ESTATÍSTICO:",
            f"   Total de critérios: {total}",
            f"   Conformes: {compliant_count} ({(compliant_count/total*100):.1f}%)",
            f"   Parciais: {partial_count} ({(partial_count/total*100):.1f}%)",
            f"   Não conformes: {non_compliant_count} ({(non_compliant_count/total*100):.1f}%)",
            ""
        ])
        
        # Avaliação geral
        if compliant_count / total >= 0.8:
            report_lines.append("AVALIAÇÃO GERAL: EXCELENTE (≥80% conforme)")
        elif compliant_count / total >= 0.6:
            report_lines.append("AVALIAÇÃO GERAL: BOM (≥60% conforme)")
        elif compliant_count / total >= 0.4:
            report_lines.append("AVALIAÇÃO GERAL: REGULAR (≥40% conforme)")
        else:
            report_lines.append("AVALIAÇÃO GERAL: CRÍTICO (<40% conforme)")
        
        return "\n".join(report_lines)
    
    def get_criterios_for_context(self) -> str:
        """Retorna critérios formatados para contexto do LLM"""
        if not self.criterios_data:
            return "ERRO: Nenhum critério JSON carregado"
        
        lines = ["=== CRITÉRIOS DE CONFORMIDADE (JSON) ===", ""]
        
        for key, value in self.criterios_data.items():
            lines.append(f"- {key.upper().replace('_', ' ')}: {value}")
        
        return "\n".join(lines)
    
    def reload_criterios(self) -> bool:
        """Recarrega critérios do arquivo JSON"""
        try:
            self.criterios_data = self._load_criterios_json()
            return True
        except Exception as e:
            logger.error(f"Erro ao recarregar critérios: {e}")
            return False

