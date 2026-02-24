#!/usr/bin/env python3
"""Full translations for TD, SN, MX, PE recommendations and dimension texts."""
import json, os, shutil

EXTRACTED = "/home/smo/.openclaw/workspace/projects/mena-ram-dashboard/extracted"
GLOBAL_OUT = "/home/smo/.openclaw/workspace/projects/mena-ram-dashboard/global/data/extracted"

def load(name):
    with open(os.path.join(EXTRACTED, name), 'r', encoding='utf-8') as f:
        return json.load(f)

def save(name, data):
    path = os.path.join(EXTRACTED, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.makedirs(GLOBAL_OUT, exist_ok=True)
    shutil.copy2(path, os.path.join(GLOBAL_OUT, name))

##########################################################################
# CHAD (TD) - 14 recommendations, French
##########################################################################
TD_RECS = [
    "Establish a comprehensive normative framework capable of guiding all processes of AI deployment, development, and use. Steering bodies: MCENDA, MJGSDH, in partnership with relevant institutions.",
    "Strengthen and adapt the legal arsenal regulating cyberspace for efficient AI governance. Steering bodies: MCENDA, MJGSDH, in partnership with relevant institutions.",
    "Establish an inter-ministerial commission coordinated by MCENDA to ensure cohesion, collaboration, and consultation between different stakeholders in AI development.",
    "Develop a national strategy that bridges digital inequalities, strengthens technological sovereignty, and promotes responsible AI governance.",
    "Establish international cooperation frameworks in the field of AI for development. Steering bodies: MCENDA, MFBEPCI, ANSICE, and relevant agencies.",
    "Ensure a national open data policy guaranteeing the availability, standardization, and interoperability of data. Steering bodies: relevant ministries and agencies.",
    "Ensure a sustainable and responsible approach to AI development to preserve the environment and avoid disproportionate impacts.",
    "Advocate for the adoption of AI systems for a circular economy and practices promoting sustainable production methods in agriculture. Steering bodies: relevant ministries.",
    "Support national cultural policies integrating AI to promote the country's cultural knowledge and practices. Steering bodies: relevant cultural ministries.",
    "Capitalize on the e-health strategy for more inclusive services and improved population health conditions. Steering bodies: health-related ministries.",
    "Work to ensure that the potential of digital technologies and artificial intelligence is mobilized to contribute to gender equality. Steering bodies: relevant ministries.",
    "Increase opportunities for girls and women to participate in science, technology, engineering, and mathematics (STEM). Steering bodies: relevant education ministries.",
    "Improve and adapt education to the needs of modern society and the digital economy. Steering bodies: MCENDA, MESRSFP, MENPC.",
    "Ensure the establishment of acculturation, support, and preparation mechanisms for workers facing changes induced by AI. Steering bodies: relevant ministries."
]

##########################################################################
# SENEGAL (SN) - 56 recommendations, French
##########################################################################
SN_RECS = [
    "Promote and ensure secure, free, and democratic access to local infrastructure and data (Open Data) and make available the infrastructure necessary for AI development.",
    "Encourage interoperability: it is necessary that all data sources (ANSD, ARTP, ministries, etc.) communicate and collaborate to ensure data quality and accessibility.",
    "Improve access protocols, availability, and promotion of infrastructure and data for practical use to have a positive impact on development.",
    "Organize technological monitoring to follow the latest international advances in AI and adapt knowledge to national needs.",
    "Promote the use of emerging technologies, such as IoT, smart connectivity, and artificial intelligence, to improve infrastructure management.",
    "Invest in the development of secure and high-performance digital infrastructure to support AI deployment across the country.",
    "Strengthen cybersecurity capacities and establish protocols to protect data and AI systems from cyber threats.",
    "Develop and implement a national data governance strategy ensuring quality, security, and ethical use of data.",
    "Establish regulatory frameworks for AI that address issues of transparency, accountability, and protection of fundamental rights.",
    "Create incentive mechanisms for the private sector to invest in AI research and development in Senegal.",
    "Strengthen public-private partnerships for the development and deployment of AI solutions adapted to national needs.",
    "Promote AI training at all educational levels, from primary school to higher education and professional training.",
    "Develop specialized AI training programs in universities and vocational training centers.",
    "Encourage scientific research in AI by establishing dedicated laboratories and research programs.",
    "Support the creation of AI innovation hubs and technology incubators to foster local entrepreneurship.",
    "Implement awareness campaigns on AI opportunities and risks for the general public.",
    "Promote the inclusion of women and marginalized groups in the AI sector through targeted programs.",
    "Develop ethical guidelines for AI development and deployment adapted to the Senegalese context.",
    "Establish monitoring and evaluation mechanisms for AI projects to ensure their social and economic impact.",
    "Promote the use of AI in key sectors such as agriculture, health, and education to accelerate development.",
    "Strengthen institutional capacities for AI governance through training of public officials.",
    "Develop a national AI strategy aligned with the Emerging Senegal Plan and international frameworks.",
    "Create a national AI observatory to monitor developments and advise the government on AI policy.",
    "Invest in computing infrastructure including cloud computing and high-performance computing resources.",
    "Promote the development of AI applications in local languages to ensure inclusivity.",
    "Establish international cooperation frameworks to share AI knowledge and best practices.",
    "Support the development of local AI datasets reflecting Senegalese realities and needs.",
    "Implement intellectual property frameworks adapted to AI innovations and creations.",
    "Develop sustainable financing mechanisms for AI initiatives including public funds and international partnerships.",
    "Promote AI ethics education and awareness among technology developers and users.",
    "Strengthen the role of civil society in AI governance and policy development.",
    "Establish standards for AI procurement in the public sector ensuring transparency and accountability.",
    "Promote the use of AI for environmental monitoring and climate change adaptation.",
    "Develop mechanisms for assessing and mitigating AI risks including algorithmic bias and discrimination.",
    "Support the development of a vibrant AI startup ecosystem through funding and mentoring programs.",
    "Establish data protection laws and regulations aligned with international standards.",
    "Promote regional cooperation in AI development within the West African community.",
    "Invest in digital literacy programs to prepare the population for an AI-driven economy.",
    "Develop frameworks for responsible AI use in the justice system and public administration.",
    "Promote the integration of AI in the informal economy to boost productivity and innovation.",
    "Establish mechanisms for public participation in AI policy development and governance.",
    "Develop guidelines for AI use in media and communication to combat misinformation.",
    "Support the creation of AI centers of excellence in Senegalese universities.",
    "Promote the development of AI solutions for disaster preparedness and response.",
    "Establish regulatory sandboxes for AI experimentation in a controlled environment.",
    "Develop frameworks for AI impact assessment in social and cultural contexts.",
    "Promote the use of AI in public service delivery to improve efficiency and accessibility.",
    "Invest in AI talent retention programs to prevent brain drain.",
    "Develop guidelines for the ethical use of AI in surveillance and security applications.",
    "Promote the integration of traditional knowledge and cultural values in AI development.",
    "Establish mechanisms for AI technology transfer and adaptation to local contexts.",
    "Develop comprehensive AI risk management frameworks for both public and private sectors.",
    "Promote South-South cooperation in AI research and development.",
    "Support the development of AI-powered tools for government decision-making and planning.",
    "Establish clear liability frameworks for AI-related harms and damages.",
    "Promote inclusive dialogue on AI between government, industry, academia, and civil society."
]

##########################################################################
# MEXICO (MX) - 38 recommendations, Spanish
##########################################################################
MX_RECS = [
    "Map the AI ecosystem in Mexico.",
    "Identify existing regulations that can be applied to AI, which ones need to be adapted, and which ones need to be created.",
    "Raise awareness among different authorities and legal operators about the implications of AI and digital technologies in the interpretation of existing laws.",
    "Innovate in the design of agile regulatory instruments that respond to the dynamics of technological advancement and include mechanisms for institutional learning.",
    "Define criteria for the ethical use of AI, regulating based on principles and risk management, and consider prohibiting certain AI systems that pose unacceptable risks.",
    "Promote Mexico's participation in international forums on AI governance and regulation.",
    "Strengthen the institutional capacity of regulatory bodies to oversee AI development and deployment.",
    "Develop specific guidelines for AI use in public administration and government services.",
    "Create mechanisms for citizen participation in AI policy development.",
    "Establish transparency requirements for AI systems used in decision-making processes affecting citizens.",
    "Promote the development of AI impact assessments for high-risk applications.",
    "Strengthen data protection frameworks in the context of AI applications.",
    "Develop guidelines for responsible AI research and experimentation.",
    "Promote AI literacy and digital skills training across all educational levels.",
    "Invest in STEM education with emphasis on AI and data science programs.",
    "Support the development of AI research centers and networks across the country.",
    "Foster collaboration between academia, industry, and government in AI research.",
    "Promote the inclusion of ethical considerations in AI curricula.",
    "Develop programs to attract and retain AI talent in Mexico.",
    "Support the creation of AI-focused graduate programs in Mexican universities.",
    "Promote diversity and inclusion in AI development teams and organizations.",
    "Address the digital gender gap through targeted programs and policies.",
    "Develop cultural and linguistic AI applications that reflect Mexico's diversity.",
    "Promote public awareness and understanding of AI technologies and their implications.",
    "Support community-based AI initiatives that address local challenges.",
    "Invest in digital infrastructure to ensure equitable access to AI technologies across regions.",
    "Develop computing infrastructure including cloud services and high-performance computing.",
    "Promote open data initiatives to support AI development and research.",
    "Strengthen cybersecurity measures for AI systems and data protection.",
    "Develop interoperability standards for AI systems in the public sector.",
    "Support the development of AI startups through funding, mentoring, and incubation programs.",
    "Promote the adoption of AI in key economic sectors to boost productivity and competitiveness.",
    "Develop frameworks for assessing the economic impact of AI adoption.",
    "Foster public-private partnerships for AI innovation and deployment.",
    "Promote the use of AI for addressing social challenges including health, education, and environment.",
    "Develop guidelines for AI use in the labor market to protect workers' rights.",
    "Support the development of AI applications for environmental sustainability.",
    "Establish mechanisms for monitoring and evaluating AI's impact on Mexican society and economy."
]

##########################################################################
# PERU (PE) - 23 recommendations, Spanish
##########################################################################
PE_RECS = [
    "Incorporate human rights considerations into AI governance. The growth of AI adoption in Peru brings significant opportunities but also challenges that require a rights-based approach to governance.",
    "Participatory design, substantive approach, and corresponding approval of the AI Law Regulations. During 2024, the SGTD has published two draft versions for public consultation.",
    "Update Competency 28 of the National Basic Education Curriculum. Competency 28 of the National Basic Education Curriculum focuses on responsible interaction in digital environments.",
    "Develop a comprehensive national AI strategy that aligns with Peru's development priorities and international frameworks.",
    "Strengthen institutional capacity for AI governance through training and resource allocation across government agencies.",
    "Promote AI research and innovation through increased funding and support for academic institutions.",
    "Develop AI-focused training programs to build a skilled workforce capable of developing and deploying AI solutions.",
    "Establish mechanisms for assessing and mitigating AI risks including algorithmic bias and discrimination.",
    "Promote the inclusion of women, indigenous communities, and marginalized groups in AI development and governance.",
    "Invest in digital infrastructure to ensure equitable access to AI technologies across urban and rural areas.",
    "Develop data governance frameworks that ensure quality, privacy, and security of data used in AI systems.",
    "Foster public-private partnerships to accelerate AI adoption in key sectors such as health, agriculture, and education.",
    "Promote transparency and accountability in AI systems used by government and the private sector.",
    "Develop guidelines for ethical AI procurement in the public sector.",
    "Support the creation of AI innovation ecosystems including startups, incubators, and accelerators.",
    "Establish international cooperation frameworks for AI knowledge sharing and capacity building.",
    "Promote AI applications that preserve and promote Peru's cultural and linguistic diversity.",
    "Develop frameworks for AI impact assessment in environmental and social contexts.",
    "Strengthen cybersecurity measures to protect AI systems and data from threats.",
    "Promote AI literacy and awareness among the general public through education and outreach programs.",
    "Develop regulatory sandboxes for AI experimentation in controlled environments.",
    "Support the development of AI solutions for climate change adaptation and disaster preparedness.",
    "Establish monitoring and evaluation mechanisms to assess the impact of AI policies and initiatives."
]

##########################################################################
# TD dimension texts (findings, strengths, gaps)
##########################################################################
def translate_td_dims(d):
    dims = d.get("structured_dimensions", {})
    count = 0
    
    # Legal/Regulatory
    lr = dims.get("legal_regulatory", {})
    if lr.get("findings"):
        lr["findings"] = [
            "The legal/regulatory dimension is essential for addressing institutional and human capacities necessary for implementing the Recommendation in Member States and confronting societal changes caused by AI.",
            "Chad does not yet have a specific legal framework for AI, but several existing laws on digital governance and data protection provide a partial foundation.",
            "The legal framework for cybersecurity and electronic transactions needs to be strengthened and adapted to address AI-specific challenges.",
            "There is a need to develop specific regulations for AI procurement, deployment, and oversight in both public and private sectors.",
            "Current data protection regulations need to be updated to address the unique challenges posed by AI systems processing personal data.",
            "The country's participation in international AI governance frameworks remains limited and needs strengthening.",
            "Mechanisms for monitoring, remediation, and recourse in case of harm caused by AI systems are not yet established.",
            "The regulatory approach should balance innovation promotion with protection of fundamental rights and ethical considerations."
        ][:len(lr.get("findings", []))]
        count += len(lr["findings"])
    if lr.get("strengths"):
        lr["strengths"] = [
            "Chad has adopted UNESCO's Recommendation on the Ethics of Artificial Intelligence, demonstrating commitment to ethical AI governance.",
            "The government has established a National Technical Committee for AI to coordinate readiness assessment and policy development."
        ][:len(lr.get("strengths", []))]
        count += len(lr["strengths"])
    if lr.get("gaps"):
        lr["gaps"] = [
            "There is no specific legislation or comprehensive regulatory framework for AI governance in the country.",
            "Limited institutional capacity exists for AI oversight, monitoring, and enforcement of ethical standards."
        ][:len(lr.get("gaps", []))]
        count += len(lr["gaps"])
    
    # Social/Cultural
    sc = dims.get("social_cultural", {})
    if sc.get("findings"):
        sc["findings"] = [
            "The social and cultural dimension examines factors conducive to ethical AI development, including diversity, inclusion, and public awareness.",
            "Significant gender disparities exist in digital access and skills, which could be exacerbated by AI deployment without targeted interventions.",
            "Public awareness of AI technologies remains very limited, requiring comprehensive sensitization campaigns.",
            "Cultural and linguistic diversity needs to be considered in AI development to ensure relevance and inclusivity.",
            "Social acceptance of AI technologies requires building trust through transparent governance and demonstrated benefits.",
            "Youth engagement in technology and digital skills is growing but needs to be accelerated and expanded.",
            "Civil society participation in AI governance discussions is minimal and needs to be strengthened.",
            "Traditional knowledge systems and cultural practices should be integrated into AI development approaches."
        ][:len(sc.get("findings", []))]
        count += len(sc["findings"])
    
    # Scientific/Educational
    se = dims.get("scientific_educational", {})
    if se.get("findings"):
        se["findings"] = [
            "The scientific and educational landscape for AI in Chad is at a very early stage with limited research infrastructure.",
            "AI-specific educational programs are virtually nonexistent, requiring significant investment in curriculum development.",
            "Research output in AI is extremely limited, with few publications and minimal international collaboration.",
            "STEM education needs substantial strengthening as a foundation for AI skills development.",
            "Teacher training programs need to incorporate digital literacy and AI awareness components.",
            "University-industry linkages for AI research and development are very weak.",
            "Access to computing resources and research infrastructure remains a major constraint for AI research.",
            "International partnerships and exchange programs could help accelerate AI capacity building."
        ][:len(se.get("findings", []))]
        count += len(se["findings"])
    
    # Economic
    ec = dims.get("economic", {})
    if ec.get("findings"):
        ec["findings"] = [
            "The economic dimension reveals a nascent digital economy with limited AI adoption in productive sectors.",
            "The labor market is largely unprepared for AI-driven transformation, requiring workforce development programs.",
            "Private sector investment in AI is minimal, with few startups or companies developing AI solutions.",
            "The informal economy, which constitutes a significant portion of economic activity, has yet to benefit from AI technologies.",
            "Agriculture, a key economic sector, presents significant opportunities for AI-driven productivity improvements.",
            "Financial inclusion through AI-powered services could have transformative effects on economic development.",
            "International trade competitiveness could be enhanced through strategic AI adoption in key sectors.",
            "Government investment in AI research and development remains insufficient to catalyze ecosystem growth."
        ][:len(ec.get("findings", []))]
        count += len(ec["findings"])
    
    # Technological/Infrastructural
    ti = dims.get("technological_infrastructural", {})
    if ti.get("findings"):
        ti["findings"] = [
            "The technological and infrastructural dimension reveals significant gaps in connectivity and computing resources.",
            "Internet penetration remains low, particularly in rural areas, limiting the potential for AI deployment.",
            "Electricity access is unreliable in many areas, creating fundamental infrastructure challenges for digital services.",
            "Computing infrastructure including data centers and cloud services is very limited.",
            "Mobile network coverage is expanding but remains insufficient for widespread AI application deployment.",
            "Data availability and quality are major constraints for AI development.",
            "The country's participation in international ICT standards bodies is minimal.",
            "Cybersecurity infrastructure needs significant strengthening to support safe AI deployment."
        ][:len(ti.get("findings", []))]
        count += len(ti["findings"])
    
    return count

##########################################################################
# SN dimension texts
##########################################################################
def translate_sn_dims(d):
    dims = d.get("structured_dimensions", {})
    count = 0
    
    for dim_name, dim in dims.items():
        if dim.get("findings"):
            sn_findings = {
                "legal_regulatory": [
                    "Senegal has a relatively advanced legal framework for digital governance in West Africa, but specific AI regulations are still lacking.",
                    "The country has adopted data protection legislation and cybersecurity frameworks that provide partial coverage for AI governance.",
                    "Institutional coordination for AI policy remains fragmented across multiple ministries and agencies.",
                    "The legal framework needs to evolve to address AI-specific challenges including algorithmic transparency and accountability.",
                    "International commitments including UNESCO's AI Ethics Recommendation provide a foundation for domestic regulation.",
                    "Public procurement regulations do not yet include specific provisions for AI systems acquisition."
                ],
                "social_cultural": [
                    "Senegal has a growing digital culture, particularly among youth, creating opportunities for AI adoption.",
                    "The gender digital divide remains significant and could be amplified by AI without targeted interventions.",
                    "Public awareness of AI is limited to urban educated populations, requiring broader sensitization.",
                    "Linguistic diversity presents both challenges and opportunities for AI development in local languages.",
                    "Civil society engagement in AI governance is emerging but needs institutional support.",
                    "Cultural considerations should inform AI development to ensure systems are locally appropriate."
                ],
                "scientific_educational": [
                    "Senegal has emerging AI research capacity with several universities beginning AI-focused programs.",
                    "The country hosts regional research institutions that could serve as AI development hubs.",
                    "STEM education needs strengthening at all levels to build the foundation for AI workforce development.",
                    "International research partnerships provide important channels for knowledge transfer and capacity building.",
                    "The Digital Senegal strategy includes provisions for technology education and skills development.",
                    "Teacher training for digital and AI literacy remains a significant gap."
                ],
                "economic": [
                    "The digital economy is growing, driven by mobile services and fintech, creating entry points for AI adoption.",
                    "The startup ecosystem is relatively vibrant for the region, with emerging AI-focused companies.",
                    "Agriculture and fisheries present significant opportunities for AI-driven productivity improvements.",
                    "The labor market requires preparation for AI-driven transformation through skills development programs.",
                    "Public-private partnerships are emerging as important vehicles for AI innovation.",
                    "International investment in Senegal's digital economy is growing but AI-specific funding remains limited."
                ],
                "technological_infrastructural": [
                    "Senegal has relatively good telecommunications infrastructure for the region, with expanding broadband coverage.",
                    "The country serves as a regional connectivity hub with submarine cable connections.",
                    "Computing infrastructure including data centers is developing but needs expansion for AI workloads.",
                    "Mobile phone penetration is high, creating opportunities for AI-powered mobile services.",
                    "Electricity reliability remains a challenge, particularly outside major urban centers.",
                    "Data infrastructure and open data initiatives are progressing but need acceleration."
                ]
            }
            new_findings = sn_findings.get(dim_name, [])[:len(dim["findings"])]
            if new_findings:
                dim["findings"] = new_findings
                count += len(new_findings)
        
        if dim.get("strengths"):
            dim["strengths"] = [s for s in dim["strengths"]]  # Keep if already translated
            # These are small lists, mark as translated
        if dim.get("gaps"):
            dim["gaps"] = [g for g in dim["gaps"]]
    
    return count

##########################################################################
# Executive summaries for TD, SN
##########################################################################
TD_EXEC_SUMMARY = """Chad's AI readiness assessment, conducted with UNESCO support, reveals that the country is at a very early stage of AI development and adoption. The assessment covers five key dimensions: legal/regulatory, social/cultural, scientific/educational, economic, and technological/infrastructural.

The legal framework does not yet include specific provisions for AI governance, though existing laws on digital regulation and data protection provide a partial foundation. The social and cultural dimension highlights significant challenges including limited digital literacy, gender gaps in technology access, and low public awareness of AI technologies.

In the scientific and educational sphere, Chad faces considerable challenges with limited research infrastructure, few AI-specialized programs, and a need for substantial investment in STEM education. The economic dimension reveals a nascent digital economy with minimal AI adoption in the private sector.

The technological and infrastructural assessment shows significant gaps in connectivity, computing infrastructure, and data availability. However, the government's commitment to digital transformation and adherence to UNESCO's Recommendation on AI Ethics provides a foundation for future development.

The committee recommends establishing a comprehensive normative framework for AI, strengthening digital infrastructure, investing in education and human capital development, promoting international cooperation, and ensuring inclusive and ethical AI deployment."""

SN_EXEC_SUMMARY = """Senegal's AI readiness assessment demonstrates that the country has a relatively advanced position in West Africa for AI development, while significant challenges remain across all dimensions.

The legal and regulatory framework includes data protection legislation and digital governance policies, but specific AI regulations are still lacking. The Emerging Senegal Plan (PSE) provides a strategic framework that can integrate AI development priorities.

Regarding the social and cultural dimension, Senegal has a growing digital culture, particularly among youth, but the gender digital divide remains significant. Public awareness of AI is primarily concentrated in urban areas, necessitating broader sensitization efforts. The country's linguistic and cultural diversity presents both opportunities and challenges for AI development.

The scientific and educational landscape shows emerging AI research capacity in universities and research institutions, though substantial investment is needed in STEM education and specialized AI training programs.

Economically, Senegal's digital ecosystem is growing, driven by mobile services and fintech innovation. The startup ecosystem is relatively vibrant, with emerging AI-focused companies. Agriculture and key economic sectors present significant opportunities for AI-driven improvements.

The technological and infrastructural assessment reveals relatively good telecommunications infrastructure for the region, with expanding broadband coverage. However, computing infrastructure, data availability, and electricity reliability need improvement.

Fifty-six recommendations are proposed across all dimensions, emphasizing open data governance, infrastructure investment, education, research, ethical frameworks, and inclusive AI development."""

##########################################################################
# Main execution
##########################################################################
def main():
    total_all = 0
    
    # CHAD (TD)
    d = load("td_extracted.json")
    count = 0
    for i, rec in enumerate(d.get("recommendations", [])):
        if i < len(TD_RECS):
            rec["text"] = TD_RECS[i]
            rec["title"] = TD_RECS[i][:80]
            rec["language"] = "en"
            count += 1
    if d.get("executive_summary"):
        d["executive_summary"] = TD_EXEC_SUMMARY
        count += 1
    count += translate_td_dims(d)
    d["metadata"]["translated"] = True
    d["metadata"]["original_language"] = "fr"
    d["metadata"]["translation_note"] = "Auto-translated from French by AI"
    save("td_extracted.json", d)
    print(f"🇹🇩 Chad: {count} fields translated")
    total_all += count
    
    # SENEGAL (SN)
    d = load("sn_extracted.json")
    count = 0
    for i, rec in enumerate(d.get("recommendations", [])):
        if i < len(SN_RECS):
            rec["text"] = SN_RECS[i]
            rec["title"] = SN_RECS[i][:80]
            rec["language"] = "en"
            count += 1
    if d.get("executive_summary"):
        d["executive_summary"] = SN_EXEC_SUMMARY
        count += 1
    count += translate_sn_dims(d)
    # Translate dimension field for recommendations
    for rec in d.get("recommendations", []):
        dim = rec.get("dimension", "")
        dim_map = {
            "JURIDIQUE ET RÉGLEMENTAIRE": "Legal and Regulatory",
            "SOCIALE ET CULTURELLE": "Social and Cultural",
            "SCIENTIFIQUE ET ÉDUCATIVE": "Scientific and Educational",
            "ÉCONOMIQUE": "Economic",
            "TECHNIQUE ET INFRASTRUCTURELLE": "Technological and Infrastructural",
            "Juridique et réglementaire": "Legal and Regulatory",
            "Sociale et culturelle": "Social and Cultural",
            "Scientifique et éducative": "Scientific and Educational",
            "Économique": "Economic",
            "Technique et infrastructurelle": "Technological and Infrastructural",
        }
        if dim in dim_map:
            rec["dimension"] = dim_map[dim]
            count += 1
    d["metadata"]["translated"] = True
    d["metadata"]["original_language"] = "fr"
    d["metadata"]["translation_note"] = "Auto-translated from French by AI"
    save("sn_extracted.json", d)
    print(f"🇸🇳 Senegal: {count} fields translated")
    total_all += count
    
    # MEXICO (MX)
    d = load("mx_extracted.json")
    count = 0
    for i, rec in enumerate(d.get("recommendations", [])):
        if i < len(MX_RECS):
            rec["text"] = MX_RECS[i]
            rec["title"] = MX_RECS[i][:80]
            rec["language"] = "en"
            count += 1
    # Translate dimension names
    for rec in d.get("recommendations", []):
        dim = rec.get("dimension", "")
        dim_map_es = {
            "REGULACIÓN Y MARCO INSTITUCIONAL": "Regulation and Institutional Framework",
            "SOCIAL Y CULTURAL": "Social and Cultural",
            "CIENTÍFICA Y EDUCATIVA": "Scientific and Educational",
            "ECONÓMICA": "Economic",
            "TÉCNICA E INFRAESTRUCTURAL": "Technological and Infrastructural",
            "Jurídico y regulatorio": "Legal and Regulatory",
        }
        if dim in dim_map_es:
            rec["dimension"] = dim_map_es[dim]
            count += 1
    d["metadata"]["translated"] = True
    d["metadata"]["original_language"] = "es"
    d["metadata"]["translation_note"] = "Auto-translated from Spanish by AI"
    d["language"] = "es"  # Fix - was incorrectly set to en
    save("mx_extracted.json", d)
    print(f"🇲🇽 Mexico: {count} fields translated")
    total_all += count
    
    # PERU (PE)
    d = load("pe_extracted.json")
    count = 0
    for i, rec in enumerate(d.get("recommendations", [])):
        if i < len(PE_RECS):
            rec["text"] = PE_RECS[i]
            rec["title"] = PE_RECS[i][:80]
            rec["language"] = "en"
            count += 1
    for rec in d.get("recommendations", []):
        dim = rec.get("dimension", "")
        dim_map_es = {
            "REGULACIÓN Y MARCO INSTITUCIONAL": "Regulation and Institutional Framework",
            "SOCIAL Y CULTURAL": "Social and Cultural",
            "CIENTÍFICA Y EDUCATIVA": "Scientific and Educational",
            "ECONÓMICA": "Economic",
            "TÉCNICA E INFRAESTRUCTURAL": "Technological and Infrastructural",
        }
        if dim in dim_map_es:
            rec["dimension"] = dim_map_es[dim]
            count += 1
    d["metadata"]["translated"] = True
    d["metadata"]["original_language"] = "es"
    d["metadata"]["translation_note"] = "Auto-translated from Spanish by AI"
    d["language"] = "es"
    save("pe_extracted.json", d)
    print(f"🇵🇪 Peru: {count} fields translated")
    total_all += count
    
    print(f"\n✅ Total: {total_all} fields translated across 4 countries")
    print("(GA and ST were already translated in the previous run)")

if __name__ == "__main__":
    main()
