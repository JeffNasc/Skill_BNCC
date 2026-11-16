# Changelog

## 1.0.2 (2026-11-15)

- `scripts/verificar_fidelidade_pdf.py` agora também confere a página: a coluna Pág. de cada habilidade precisa coincidir com o número impresso no rodapé da página do PDF onde o código aparece. Resultado atual: 0 divergências em 1.576.
- `tests/regressao.py` ampliado: códigos inexistentes de vários formatos, códigos semelhantes, componentes do 6º ano e coluna "Aplica-se aos anos".

## 1.0.1 (2026-11-15)

- Correção de texto: EF03LP11 trazia "gráficovisuais"; o PDF oficial traz "gráfico-visuais". Achado pelo novo script de fidelidade.
- Novo `scripts/verificar_fidelidade_pdf.py`: confere o texto de todas as habilidades contra os PDFs oficiais (EF por palavras na coluna de habilidades das páginas do código; EI e EM por texto contínuo). Resultado atual: 0 divergências em 1.576.
- Novo `tests/regressao.py`: 13 testes automáticos dos fatos que os casos do manual esperam, executados a cada push.
- SKILL.md: Língua Portuguesa deve reunir os três blocos do ano (EF12/EF15 e EF02); código inexistente gera pergunta de ano e tema, sem sugestão de tema não citado; pedido amplo de editor gera pergunta de etapa e componente.
- Achados de uma avaliação independente (nota preliminar 8,2/10) incorporados ao manual de teste.

## 1.0.0 (2026-11-15)

- Base com 1.576 habilidades: Educação Infantil (93), Ensino Fundamental (1.304) e Ensino Médio (179), com texto literal, código e página do PDF oficial.
- Unidade temática e objeto de conhecimento no Ensino Fundamental; competências específicas no topo de cada área do Ensino Médio.
- Coluna "Aplica-se aos anos" e Língua Portuguesa dividida por bloco de anos.
- Adaptadores para GPT e Copilot.
- Scripts de extração e validação contra os PDFs oficiais.
- Limite: o complemento de Computação (2022) não está incluído. Previsto para a versão 1.1, a partir do anexo oficial.
