#!/usr/bin/env python3
"""Translate RAM extracted JSONs from FR/PT/ES to English."""
import json, os, re, copy, shutil

EXTRACTED = "/home/smo/.openclaw/workspace/projects/mena-ram-dashboard/extracted"
GLOBAL_OUT = "/home/smo/.openclaw/workspace/projects/mena-ram-dashboard/global/data/extracted"

# Manual translations for each country
# We'll do inline translations since these are domain-specific UNESCO AI readiness texts

def translate_ga(data):
    """Translate Gabon (French)"""
    counts = {"recommendations": 0, "executive_summary": 0, "findings": 0, "strengths": 0, "gaps": 0, "regulations": 0, "achievements": 0, "rankings": 0, "key_numbers": 0}
    
    # Executive summary
    data["executive_summary"] = """EXECUTIVE SUMMARY

Following the adoption of the Recommendation on the Ethics of Artificial Intelligence, UNESCO has provided support to various Member States, including Gabon, in the process of assessing AI readiness. In response, the government, with UNESCO's support, established the National Technical Committee for AI (CTN-IA). Composed of members from ministries directly involved in AI issues, this committee carried out preparatory work for the implementation of the assessment process.

The assessment reveals that the implementation of AI systems in Gabon remains embryonic. While no AI use cases have yet been identified in public administration, there is nonetheless some activity in the private and semi-public sectors, particularly in teaching, research and learning, in the productive sector, and in individual usage through various tools, including social networks that have integrated AI into their programming.

These early stages of AI usage require measures to be taken to enable AI development.

From a legal perspective, a framework exists, often linked to digital technology. Not directly related to AI, this legal framework capable of governing the ethical deployment of AI would benefit from evolving to address the challenges raised by AI.

The social/cultural dimension reveals a small gender gap in internet access in Gabon. While no provisions exist to reduce the digital gender gap, there are provisions aimed at reducing the socio-economic digital gap and the gap between rural and urban areas. Private and semi-public initiatives are also noteworthy, aimed at increasing diversity in the AI sector. Regarding public engagement and trust in digital technology, while it still needs significant improvement, it has noticeably increased over the past two decades. However, significant efforts remain to improve the ethical deployment of AI in the environment, culture, health, and social well-being.

For the scientific and educational dimension, a proactive policy must be implemented so that research and innovation can benefit from the opportunities offered by AI. The same applies to education, where existing infrastructure and systems do not allow for optimal deployment of AI in this sector.

Regarding the economic dimension, the size and robustness of the AI ecosystem are insignificant. Similarly, the consideration of AI specifics in available statistics is not noticeable.

Finally, the analysis of the technical and infrastructural dimension reveals an acceptable situation regarding infrastructure and good connectivity. Gabon would benefit from being more present in international normative bodies in the ICT sector. Efforts should also be made to strengthen the country's computing capabilities and improve its statistical performance."""
    counts["executive_summary"] = 1
    
    # Recommendations
    recs_en = [
        "Establishment of an ad hoc committee for the definition of AI strategy, supported by an expert;",
        "Establishment of a National Council dedicated to monitoring and controlling the implementation of the national AI strategy;",
        "Involvement of all other ministries as partners in implementing the said strategy for inclusivity purposes."
    ]
    for i, rec in enumerate(data.get("recommendations", [])):
        if i < len(recs_en):
            rec["text"] = recs_en[i]
            rec["title"] = recs_en[i]
            rec["language"] = "en"
            counts["recommendations"] += 1
    
    # Structured dimensions findings/strengths/gaps
    dims = data.get("structured_dimensions", {})
    
    # Legal/Regulatory
    lr = dims.get("legal_regulatory", {})
    lr_findings_en = [
        "The legal/regulatory dimension is essential for addressing the question of institutional and human capacities necessary for implementing the Recommendation in Member States and, more generally, for confronting the profound societal upheavals caused by AI.",
        "Numerous legal provisions with an indirect impact on AI regulation have been identified.",
        "In terms of education and research, Law No. 21/2011 on the general orientation of education, training and research has an indirect impact on AI-related regulations.",
        "Finally, Law No. 3/91 of March 26, 1991, relating to the Constitution of the Gabonese Republic, sets out several principles with an impact on AI-related regulation.",
        "Gabon does not have laws or policies relating to the procurement of AI systems or products/services containing AI elements.",
        "Individuals have the ability under this same law to request information on how AI systems are used in the public sector.",
        "It should be noted that no law or policy details the mechanisms for monitoring, remediation and recourse in case of harm caused by AI systems.",
        "However, while no provisions regarding the impact of AI on social networks, particularly concerning transparency, disinformation, false information and hate speech, are clearly stated, the Communication Code in its Article 114 addresses this."
    ]
    lr_strengths_en = [
        "At the international level, Gabon has not yet adopted binding or non-binding regulations specific to AI.",
        "However, Gabon, like the 192 other UNESCO Member States, adopted the very first global standard on the Ethics of Artificial Intelligence presented by UNESCO at the General Conference of the United Nations for Education, Science and Culture, held in Paris."
    ]
    for i, f in enumerate(lr.get("findings", [])):
        if i < len(lr_findings_en):
            lr["findings"][i] = lr_findings_en[i]
            counts["findings"] += 1
    for i, s in enumerate(lr.get("strengths", [])):
        if i < len(lr_strengths_en):
            lr["strengths"][i] = lr_strengths_en[i]
            counts["strengths"] += 1
    
    # Social/Cultural
    sc = dims.get("social_cultural", {})
    sc_findings_en = [
        "The Social/Cultural dimension examines factors conducive to the ethical development and deployment of AI systems, including social and cultural inclusion and diversity, public awareness, and the values necessary for the widespread adoption of ethical AI solutions.",
        "In other words, if AI development and deployment teams are very homogeneous, AI systems may not adequately reflect the complexity and diversity of society.",
        "Products generated by AI systems could then exacerbate structural biases.",
        "Furthermore, this section examines attitudes towards AI technologies, including their public acceptance.",
        "Moreover, while no specific law exists, public initiatives through SING and INPTIC, and private ones through Mindset Magazine and the Robotics Club, aim to increase diversity in the AI sector.",
        "As for Mindset magazine (quarterly: https://mindsetmag.online/), it addresses not only AI-related issues but also specifies gender aspects.",
        "The magazine is an emanation of the Think Tank called Institut TIS (Technology, Innovation and Sciences) with the ambition of monitoring the AI domain and providing responses to research and analysis requests from public administration clients.",
        "Regarding languages, online content and data intended for training AI systems are available in French, the official language of Gabon."
    ]
    sc_gaps_en = [
        "Regarding the Facebook Gender Gap Index, data from countries around the world on the total number of female and male monthly active Facebook users is collected via the marketing API.",
        "Using these aggregated figures, the Facebook Gender Gap Index is generated."
    ]
    for i, f in enumerate(sc.get("findings", [])):
        if i < len(sc_findings_en):
            sc["findings"][i] = sc_findings_en[i]
            counts["findings"] += 1
    for i, g in enumerate(sc.get("gaps", [])):
        if i < len(sc_gaps_en):
            sc["gaps"][i] = sc_gaps_en[i]
            counts["gaps"] += 1
    
    # Economic
    ec = dims.get("economic", {})
    ec_findings_en = [
        "Her foresight and commitment to AI have most likely contributed to the mobilization of her ministry's staff and its autonomous entities for data collection used in this assessment.",
        "We also extend our thanks to other stakeholders, particularly the private sector, through mobile telephony and internet service provider companies, which were represented at the highest level during the data collection workshop.",
        "AI-based tools and applications make our lives easier, smoother, and richer.",
        "But in its current form, AI reproduces and amplifies many of the social challenges we face.",
        "To shape the technological development of AI, we need effective governance frameworks, supported by the ethical and moral values that are dear to all of us.",
        "This is why UNESCO developed the Recommendation on the Ethics of Artificial Intelligence, which 193 countries have adopted to ensure that AI produces equitable, sustainable, and inclusive results.",
        "While AI is generally at an embryonic stage in Gabon, the early signs we observe must be properly regulated.",
        "For example, Gabon's current legal framework, while consistent with digital technology, must align with the specificities of AI."
    ]
    ec_strengths_en = [
        "This is why our country Gabon, like the 192 other UNESCO Member States, adopted the very first global standard on the Ethics of Artificial Intelligence presented by UNESCO at the General Conference of the United Nations for Education, Science and Culture.",
        "Today's meeting is a positive response to the call to action, launched to guarantee a future where AI serves humanity, contributing to the achievement of the Sustainable Development Goals, fostering innovation and progress, while ensuring respect for ethical values.",
        "In response, the government with UNESCO's support established the National Technical Committee for AI (CTN-IA)."
    ]
    ec_gaps_en = [
        "However, even in the absence of a defined AI strategy, the government's willingness to apply the Recommendation on the Ethics of Artificial Intelligence should be noted."
    ]
    for i, f in enumerate(ec.get("findings", [])):
        if i < len(ec_findings_en):
            ec["findings"][i] = ec_findings_en[i]
            counts["findings"] += 1
    for i, s in enumerate(ec.get("strengths", [])):
        if i < len(ec_strengths_en):
            ec["strengths"][i] = ec_strengths_en[i]
            counts["strengths"] += 1
    for i, g in enumerate(ec.get("gaps", [])):
        if i < len(ec_gaps_en):
            ec["gaps"][i] = ec_gaps_en[i]
            counts["gaps"] += 1
    
    # key_numbers - already in English
    
    # Metadata
    data["metadata"]["translated"] = True
    data["metadata"]["original_language"] = "fr"
    data["metadata"]["translation_note"] = "Auto-translated from French by AI"
    
    total = sum(counts.values())
    return data, counts, total


def translate_st(data):
    """Translate São Tomé (Portuguese)"""
    counts = {"recommendations": 0, "executive_summary": 0, "findings": 0, "strengths": 0, "gaps": 0, "regulations": 0, "achievements": 0, "rankings": 0, "key_numbers": 0}
    
    recs_en = [
        ("Update of Law No. 07/2017 – Law on the Organization and Functioning of the National Personal Data Protection Agency (Actualização da Lei n.º 07/2017)", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Update of Decree-Law 19/2008, which creates INIC (Actualização do Decreto-Lei 19/2008)", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Update of Resolution No. 35/2020 of the Council of Ministers, adopting the National Digital Governance Strategy (Actualização da Resolução n.º 35/2020)", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Strengthening the capacity of the National Statistics Institute (INE)", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Update of the Educational Policy Charter (CPE) (Actualização da Carta de Política Educativa)", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Organization of a seminar on AI development and Ethics", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Creation of personal data protection and AI ethics professionals", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Improvement of the telecommunications ecosystem", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Adoption of a radio and television information and awareness program", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
        ("Approval of the National AI Strategy Law (Aprovação da Lei da Estratégia Nacional de IA)", "REGULATION AND INSTITUTIONAL FRAMEWORK"),
    ]
    for i, rec in enumerate(data.get("recommendations", [])):
        if i < len(recs_en):
            rec["text"] = recs_en[i][0]
            rec["title"] = recs_en[i][0]
            rec["dimension"] = recs_en[i][1]
            rec["language"] = "en"
            counts["recommendations"] += 1
    
    data["metadata"]["translated"] = True
    data["metadata"]["original_language"] = "pt"
    data["metadata"]["translation_note"] = "Auto-translated from Portuguese by AI"
    
    total = sum(counts.values())
    return data, counts, total


def process_country(filename, translate_fn):
    filepath = os.path.join(EXTRACTED, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data, counts, total = translate_fn(data)
    
    # Save back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Copy to global
    os.makedirs(GLOBAL_OUT, exist_ok=True)
    shutil.copy2(filepath, os.path.join(GLOBAL_OUT, filename))
    
    return counts, total


# For the large files (MA, TD, SN, MX, PE), we need to read and translate them too.
# Let's output a helper script that does targeted translations using the JSON structure.

def load_json(name):
    with open(os.path.join(EXTRACTED, name), 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(name, data):
    path = os.path.join(EXTRACTED, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.makedirs(GLOBAL_OUT, exist_ok=True)
    shutil.copy2(path, os.path.join(GLOBAL_OUT, name))


if __name__ == "__main__":
    # Process GA
    counts_ga, total_ga = process_country("ga_extracted.json", translate_ga)
    print(f"🇬🇦 Gabon: {total_ga} fields translated - {counts_ga}")
    
    # Process ST
    counts_st, total_st = process_country("st_extracted.json", translate_st)
    print(f"🇸🇹 São Tomé: {total_st} fields translated - {counts_st}")
    
    print("\n--- GA and ST done. Large files need separate processing. ---")
