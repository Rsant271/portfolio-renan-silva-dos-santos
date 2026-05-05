"""
Gerador do CV em PDF — Renan Silva dos Santos
Disciplina: Programação de Computadores (UNICID 2026.1)

Gera o arquivo Renan_Silva_dos_Santos_CV.pdf na mesma pasta deste script.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
)

# ===================== CONFIG =====================
NOME_COMPLETO = "Renan Silva dos Santos"
EMAIL = "comprasrsant@gmail.com"
CIDADE = "São Paulo, SP"
LINKEDIN = "linkedin.com/in/renan-santos-7584901a1"
GITHUB = "github.com/Rsant271"
ARQUIVO_SAIDA = "Renan_Silva_dos_Santos_CV.pdf"
# ==================================================


def gerar_cv():
    cor_primaria = HexColor("#1a1a1a")
    cor_secundaria = HexColor("#555555")

    doc = SimpleDocTemplate(
        ARQUIVO_SAIDA,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"{NOME_COMPLETO} - Currículo",
        author=NOME_COMPLETO,
        subject="Currículo Profissional",
    )

    styles = getSampleStyleSheet()

    style_nome = ParagraphStyle(
        "Nome", parent=styles["Heading1"],
        fontSize=24, textColor=cor_primaria, spaceAfter=4, alignment=TA_LEFT,
    )
    style_contato = ParagraphStyle(
        "Contato", parent=styles["Normal"],
        fontSize=10, textColor=cor_secundaria, spaceAfter=2,
    )
    style_secao = ParagraphStyle(
        "Secao", parent=styles["Heading2"],
        fontSize=13, textColor=cor_primaria, spaceBefore=12, spaceAfter=6,
    )
    style_subtitulo = ParagraphStyle(
        "Subtitulo", parent=styles["Normal"],
        fontSize=11, textColor=cor_primaria, fontName="Helvetica-Bold",
        spaceAfter=2,
    )
    style_corpo = ParagraphStyle(
        "Corpo", parent=styles["Normal"],
        fontSize=10, textColor=cor_primaria, leading=14, spaceAfter=4,
    )
    style_meta = ParagraphStyle(
        "Meta", parent=styles["Normal"],
        fontSize=9, textColor=cor_secundaria, spaceAfter=4,
    )

    elementos = []

    # Cabeçalho
    elementos.append(Paragraph(NOME_COMPLETO, style_nome))
    elementos.append(Paragraph(
        f"{CIDADE} &nbsp;·&nbsp; {EMAIL}",
        style_contato,
    ))
    elementos.append(Paragraph(f"{LINKEDIN} &nbsp;·&nbsp; {GITHUB}", style_contato))
    elementos.append(Spacer(1, 6))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=cor_secundaria))
    elementos.append(Spacer(1, 6))

    # Resumo Profissional
    elementos.append(Paragraph("Resumo Profissional", style_secao))
    elementos.append(Paragraph(
        "Profissional de marketing digital com atuação em tráfego pago, automação de processos "
        "e Inteligência Artificial aplicada ao atendimento e vendas. Atualmente cursando Análise "
        "e Desenvolvimento de Sistemas para aprofundar a parte técnica, com foco em IA, automações "
        "e ciência de dados.",
        style_corpo,
    ))

    # Experiência Profissional
    elementos.append(Paragraph("Experiência Profissional", style_secao))
    elementos.append(Paragraph(
        "Profissional de Marketing — Clínica Meneghini Odontologia",
        style_subtitulo,
    ))
    elementos.append(Paragraph("2024 — atual &nbsp;·&nbsp; São Paulo, SP", style_meta))
    itens_exp = [
        "<b>Tráfego pago:</b> gestão de campanhas no Meta Ads e Google Ads, "
        "com foco em geração de leads qualificados e otimização de custo por conversão.",
        "<b>Automação:</b> criação de fluxos no n8n integrando WhatsApp, CRM e banco de dados "
        "para qualificar leads e reduzir trabalho manual da recepção.",
        "<b>Inteligência Artificial:</b> implementação de agente conversacional de IA no WhatsApp "
        "para atendimento inicial, qualificação e agendamento de pacientes.",
        "<b>CRM:</b> organização e gestão do pipeline de pacientes no HubSpot — segmentação, "
        "acompanhamento de jornada e relatórios de conversão.",
        "<b>Conteúdo e criativos:</b> produção de roteiros, posts e criativos para campanhas, "
        "alinhados ao posicionamento da clínica.",
    ]
    elementos.append(ListFlowable(
        [ListItem(Paragraph(item, style_corpo)) for item in itens_exp],
        bulletType="bullet", leftIndent=14,
    ))

    # Formação Acadêmica
    elementos.append(Paragraph("Formação Acadêmica", style_secao))
    elementos.append(Paragraph(
        "Análise e Desenvolvimento de Sistemas — Graduação", style_subtitulo,
    ))
    elementos.append(Paragraph(
        "Universidade Cidade de São Paulo (UNICID — Cruzeiro do Sul Educacional)",
        style_corpo,
    ))
    elementos.append(Paragraph("2026 — atual &nbsp;·&nbsp; 1º semestre", style_meta))
    elementos.append(Paragraph(
        "<b>Disciplinas em curso:</b> Engenharia de Prompt e Aplicações em IA, "
        "Interface e Jornada do Usuário, Programação de Computadores, "
        "Prototipagem de Sistemas Computacionais, Humanidades e as Populações Brasileiras.",
        style_corpo,
    ))

    # Conhecimentos Técnicos
    elementos.append(Paragraph("Conhecimentos Técnicos", style_secao))
    itens_tec = [
        "<b>Marketing digital:</b> Meta Ads, Google Ads, GTM, GA4, Conversions API",
        "<b>Automação:</b> n8n, integrações via webhook e API",
        "<b>Inteligência Artificial:</b> engenharia de prompt, modelos LLM (Claude, GPT, Gemini), agentes de IA",
        "<b>CRM &amp; Dados:</b> HubSpot, Supabase, planilhas avançadas",
        "<b>Programação (em estudo):</b> Python, JavaScript, HTML/CSS, lógica de programação",
        "<b>Ferramentas:</b> Figma, Git, GitHub, VS Code",
        "<b>Idiomas:</b> Português (nativo), Inglês (básico)",
    ]
    elementos.append(ListFlowable(
        [ListItem(Paragraph(item, style_corpo)) for item in itens_tec],
        bulletType="bullet", leftIndent=14,
    ))

    # Projetos Acadêmicos
    elementos.append(Paragraph("Projetos Acadêmicos", style_secao))
    elementos.append(Paragraph(
        "Projeto Promptzeiros — Engenharia de Prompt e Aplicações em IA (2026)",
        style_subtitulo,
    ))
    elementos.append(Paragraph(
        "Projeto integrador em grupo da disciplina de Engenharia de Prompt. "
        "Construção de prompts estruturados e desenvolvimento de agente conversacional "
        "com integração WhatsApp, banco de dados e fluxos automatizados via n8n.",
        style_corpo,
    ))

    # Habilidades Comportamentais
    elementos.append(Paragraph("Habilidades Comportamentais", style_secao))
    itens_soft = [
        "Aprendizado autodidata",
        "Resolução de problemas",
        "Trabalho em equipe",
        "Visão de negócio aplicada à tecnologia",
        "Curiosidade técnica",
    ]
    elementos.append(ListFlowable(
        [ListItem(Paragraph(item, style_corpo)) for item in itens_soft],
        bulletType="bullet", leftIndent=14,
    ))

    doc.build(elementos)
    print(f"PDF gerado: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    gerar_cv()
