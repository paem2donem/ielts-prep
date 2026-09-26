"""
IELTS Exam Materials Repository
Contains authentic Cambridge Academic and Cyber Forensics / Jean Monnet modules for:
- Listening (Sections 1-4 with audio scripts and questions)
- Reading (Passages with True/False/Not Given and Multiple Choice)
- Writing (Task 1 Academic Data/Process + Task 2 Discursive Essay)
- Speaking (Parts 1, 2 Cue Card, 3 Discussion)
"""

EXAM_DATA = {
    "cyber": {
        "title": "Adli Bilişim & Jean Monnet Siber Güvenlik Modu",
        "description": "Europol EC3 ve Jean Monnet standartlarında adli bilişim ve siber hukuk odaklı sınav seti.",
        "listening": {
            "section_1": {
                "id": "cyber_l1",
                "title": "Section 1: Cyber Incident Response Hotline Report",
                "intro": "You will hear a conversation between an IT Security Manager and a Europol Incident Response Officer recording a ransomware breach.",
                "audio_script": """
Officer: Good morning, Europol Cyber Incident Response Unit. Officer Davies speaking. How can I assist you today?
Manager: Hello Officer. I am calling from FinTech Vault in Amsterdam. We detected an unauthorized intrusion and ransomware deployment across our active cluster this morning.
Officer: Understood. Let's record the critical details for our forensic triage. First, what is your company's full registration name?
Manager: It is FinTech Vault B.V.
Officer: And what is your primary point of contact phone number and extension?
Manager: My mobile is +31 20 555 0194, extension 402.
Officer: Got that. What time was the anomalous activity first flagged by your SIEM system?
Manager: It was flagged at 03:45 AM Central European Time.
Officer: What specific ransomware strain or signature extension was appended to the encrypted files?
Manager: The encrypted files carry the extension dot-lock-bit, specifically '.lockbit3'.
Officer: And did the threat actors leave a ransom note? What is the cryptocurrency wallet address indicated?
Manager: Yes, they demanded payment in Monero, address ending in 8X9W.
Officer: Crucially, was the affected partition isolated from the wide area network, and did you preserve the volatile RAM image before rebooting?
Manager: Yes, our incident handler immediately dumped the RAM using LiME forensic tool and pulled the network cables without shutting down the hypervisor.
Officer: Excellent, that preserves the chain of custody. A forensic analyst from our team will arrive within two hours.
""",
                "questions": [
                    {
                        "id": "cl1_q1",
                        "type": "fill",
                        "prompt": "1. Company Name: FinTech ____________ B.V.",
                        "answer": "Vault",
                        "accepted": ["vault", "Vault"]
                    },
                    {
                        "id": "cl1_q2",
                        "type": "fill",
                        "prompt": "2. Time of initial detection: ____________ AM CET",
                        "answer": "03:45",
                        "accepted": ["03:45", "3:45", "03:45 AM", "3:45 AM"]
                    },
                    {
                        "id": "cl1_q3",
                        "type": "fill",
                        "prompt": "3. File encryption extension: .____________",
                        "answer": "lockbit3",
                        "accepted": ["lockbit3", "lockbit", ".lockbit3"]
                    },
                    {
                        "id": "cl1_q4",
                        "type": "fill",
                        "prompt": "4. Forensic memory acquisition tool used: ____________",
                        "answer": "LiME",
                        "accepted": ["lime", "LiME", "LIME"]
                    }
                ]
            },
            "section_2": {
                "id": "cyber_l2",
                "title": "Section 2: Europol Cyber Training Academy Orientation",
                "intro": "You will hear a director presenting the facilities and security protocols at the European Cybercrime Training Center in The Hague.",
                "audio_script": """
Welcome ladies and gentlemen to the European Cybercrime Centre Training Facility. As forensic investigators and Jean Monnet scholars, you are entering a high-security zone.
Before we commence our practical exercises in memory acquisition and hardware reverse-engineering, observe three mandatory protocols.
First, all personal electronic devices—smartphones, smartwatches, and external flash drives—must be deposited in the Faraday cages located directly to the right of the reception foyer. Radio frequency signals must not penetrate our clean testing environment.
Second, the digital forensic sandbox on the second floor operates on an air-gapped subnet. Under no circumstances should any bridge interface be created to the commercial internet.
Third, evidence handling adheres strictly to ISO/IEC 27037. When you check out physical drives or cloned images from the Evidence Vault, you must scan your biometric badge and record the SHA-256 checksum on the tamper-evident ledger.
Now, if you look at the floor plan, the hardware teardown laboratory is located in Room 204, while the digital evidence deposition mock courtroom is situated in the west wing, adjacent to the auditorium.
""",
                "questions": [
                    {
                        "id": "cl2_q1",
                        "type": "mcq",
                        "prompt": "5. Personal devices must be deposited in:",
                        "options": ["A) The reception lockers", "B) The Faraday cages", "C) The Evidence Vault"],
                        "answer": "B",
                        "explanation": "Personal electronic devices must be deposited in Faraday cages to prevent radio frequency penetration."
                    },
                    {
                        "id": "cl2_q2",
                        "type": "mcq",
                        "prompt": "6. The digital forensic sandbox on the second floor is:",
                        "options": ["A) Connected to Europol intranet", "B) Monitored by live AI", "C) Air-gapped from the internet"],
                        "answer": "C",
                        "explanation": "The speaker states the sandbox operates on an air-gapped subnet with no bridge to the commercial internet."
                    },
                    {
                        "id": "cl2_q3",
                        "type": "mcq",
                        "prompt": "7. When taking evidence from the vault, scholars must verify:",
                        "options": ["A) The SHA-256 checksum", "B) The police warrant", "C) The vendor warranty"],
                        "answer": "A",
                        "explanation": "Scholars must record the SHA-256 checksum on the tamper-evident ledger."
                    }
                ]
            }
        },
        "reading": {
            "passage_1": {
                "title": "Passage 1: ISO/IEC 27037 & The Evolution of Digital Evidence Admissibility",
                "text": """
The legal and procedural framework governing digital forensics has undergone radical evolution since the inception of computer-related jurisprudence. Traditionally, law enforcement relied on static post-mortem analysis: seizing a desktop tower, removing the physical hard drive, connecting it to a hardware write-blocker, and generating a bit-stream disk duplicate verified by an MD5 or SHA-1 cryptographic hash. These foundational protocols were formalized under international standard ISO/IEC 27037, which establishes explicit guidelines for the identification, collection, acquisition, and preservation of digital evidence.

However, the rapid migration of modern corporate architecture to volatile cloud environments and non-volatile Solid State Drives (SSDs) possessing TRIM and wear-leveling algorithms has rendered static disk imaging insufficient. In enterprise ransomware investigations, threat actors frequently employ memory-only malware—or 'fileless' attacks—that reside exclusively within volatile RAM. If an investigator disconnects power to preserve storage media according to outdated manual protocols, critical volatile artifacts (including cryptographic session keys, active network socket bindings, and decrypted ransomware master keys) are instantaneously and irreversibly lost.

Consequently, modern forensic methodology prioritizes 'Live Response' over static triage. Live forensic acquisition requires the investigator to interact directly with the running operational environment, thereby inevitably introducing minuscule modifications to the target host's kernel and unallocated memory. Defense attorneys in criminal and corporate litigation frequently seize upon these state alterations, claiming that the 'Chain of Custody' has been compromised and demanding the judicial exclusion of digital evidence under the Daubert or Frye admissibility doctrines.

To mitigate such evidentiary challenges, forensic practitioners must demonstrate adherence to deterministic reproducibility. By calculating real-time dual-hashing (SHA-256 and SHA-512) and documenting an exhaustive audit trail with microsecond timestamp synchronization, investigators provide incontrovertible mathematical verification that the substantive content of acquired evidence remains untainted.
""",
                "questions": [
                    {
                        "id": "cr_q1",
                        "prompt": "1. ISO/IEC 27037 guidelines were primarily developed for static storage media rather than live cloud triage.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "TRUE",
                        "explanation": "Metin geleneksel statik sürücü protokollerinin ISO/IEC 27037 altında resmileştirildiğini doğrular."
                    },
                    {
                        "id": "cr_q2",
                        "prompt": "2. Disconnecting power from a computer infected with fileless malware ensures safe recovery of decryption keys.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "FALSE",
                        "explanation": "Metinde sistemin gücünü kesmenin RAM'deki uçucu anahtarları kalıcı olarak yok edeceği (irreversibly lost) belirtilmiştir."
                    },
                    {
                        "id": "cr_q3",
                        "prompt": "3. The majority of European judges prefer MD5 hashing over SHA-256 for judicial admissibility.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "NOT GIVEN",
                        "explanation": "Avrupalı hakimlerin tercihleri hakkında metinde bir bilgi verilmemiştir."
                    },
                    {
                        "id": "cr_q4",
                        "prompt": "4. Live forensic analysis inevitably causes slight state modifications on the inspected system.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "TRUE",
                        "explanation": "Metinde 'inevitably introducing minuscule modifications to the target host' ifadesi açıkça yer almaktadır."
                    }
                ]
            }
        },
        "writing": {
            "task_1": {
                "title": "Task 1 (Report - 150 Words)",
                "prompt": """
The bar chart illustrates the average time taken (in hours) to identify, isolate, and acquire forensic images from compromised cloud virtual machines across four European countries (Germany, France, Netherlands, Estonia) between 2020 and 2024.

Summarise the information by selecting and reporting the main features, and make comparisons where relevant.
Write at least 150 words.
""",
                "data_context": "Data summary: Estonia consistently achieved the fastest response times (decreasing from 4.2 hours in 2020 to 1.1 hours in 2024). Germany experienced gradual reduction from 8.5 to 3.8 hours. The Netherlands improved from 6.0 to 2.4 hours, while France had the slowest average in 2024 at 4.6 hours."
            },
            "task_2": {
                "title": "Task 2 (Essay - 250 Words)",
                "prompt": """
In criminal investigations, law enforcement agencies are increasingly utilizing automated AI surveillance software and algorithmic evidence-gathering tools to combat transnational cybercrime.

While proponents assert that these technologies are indispensable for public safety, critics argue that they severely infringe upon fundamental privacy rights and jeopardize fair trial principles.

Discuss both views and give your own reasoned opinion, specifically addressing the legal admissibility of algorithmically obtained digital evidence.
Write at least 250 words.
"""
            }
        },
        "speaking": {
            "part_1": {
                "title": "Part 1: Background & Specialization",
                "questions": [
                    "Can you introduce yourself and explain what sparked your interest in digital forensics and cyber security?",
                    "What specific tools or forensic techniques do you use most frequently?",
                    "How has cyber investigation changed in your country over the last five years?"
                ]
            },
            "part_2": {
                "title": "Part 2: Cue Card (Long Turn)",
                "cue_card": """
Describe a complex cyber security challenge or forensic case you have studied or encountered.

You should say:
• What the nature of the cyber incident or forensic problem was
• What methodologies or technical tools were applied to resolve it
• What legal or ethical obstacles (such as chain of custody or privacy laws) arose
And explain what crucial lesson you derived from this experience for modern forensic science.
""",
                "prep_time": 60,
                "speak_time": 120
            },
            "part_3": {
                "title": "Part 3: In-Depth Discussion",
                "questions": [
                    "How do cloud computing architectures complicate the legal concept of territorial sovereignty when seizing digital evidence?",
                    "To what extent will artificial intelligence and automated deepfake generation undermine the trustworthiness of electronic evidence in court?",
                    "What reforms are urgently required in international Mutual Legal Assistance Treaties (MLATs) to speed up cross-border cyber prosecutions?"
                ]
            }
        }
    },
    "academic": {
        "title": "Genel Cambridge IELTS Academic Modu",
        "description": "Standart Cambridge IELTS sınav formatında çevre, bilim, eğitim ve toplum temalı sınav seti.",
        "listening": {
            "section_1": {
                "id": "acad_l1",
                "title": "Section 1: University Accommodation Registration",
                "intro": "You will hear a prospective international student inquiring about postgraduate campus accommodation.",
                "audio_script": """
Clerk: Good afternoon, University Student Housing Office. How can I help you today?
Student: Hello, my name is Alex Turner. I have been accepted into the Master's in Data Science program, and I would like to register for campus housing.
Clerk: Excellent, Alex. Let me pull up the registration form. Could you give me your student identification number?
Student: Yes, it is S-D-9-4-1-8-8.
Clerk: SD94188. And what is your preferred room category? We offer single ensuite rooms, shared double apartments, and family studios.
Student: I would prefer a single ensuite room with a quiet study desk.
Clerk: Very well. Single ensuite rooms are located in Darwin Hall and Newton Court. Newton Court has access to the university gym and bicycle storage.
Student: Newton Court sounds ideal. What is the weekly rental fee for that?
Clerk: The weekly rent is 165 pounds, which includes all utilities, high-speed fiber internet, and heating.
Student: That fits my budget. When is the deposit due?
Clerk: You will need to pay a refundable deposit of 300 pounds by the 15th of August to guarantee your placement.
""",
                "questions": [
                    {
                        "id": "al1_q1",
                        "type": "fill",
                        "prompt": "1. Student ID Number: SD____________",
                        "answer": "94188",
                        "accepted": ["94188"]
                    },
                    {
                        "id": "al1_q2",
                        "type": "fill",
                        "prompt": "2. Preferred Room Type: Single ____________",
                        "answer": "ensuite",
                        "accepted": ["ensuite", "en-suite", "Ensuite"]
                    },
                    {
                        "id": "al1_q3",
                        "type": "fill",
                        "prompt": "3. Selected Hall of Residence: ____________ Court",
                        "answer": "Newton",
                        "accepted": ["newton", "Newton"]
                    },
                    {
                        "id": "al1_q4",
                        "type": "fill",
                        "prompt": "4. Weekly rental fee: £____________",
                        "answer": "165",
                        "accepted": ["165", "165 pounds"]
                    }
                ]
            }
        },
        "reading": {
            "passage_1": {
                "title": "Passage 1: The Transition to Grid-Scale Renewable Energy Storage",
                "text": """
The transition from fossil-fuel-dominated power generation to decentralized renewable energy sources—principally solar photovoltaic and wind turbine arrays—represents one of the grandest engineering challenges of the twenty-first century. While the capital expenditure for solar modules and wind generators has plummeted by more than eighty percent over the past decade, renewable power faces an intrinsic vulnerability: intermittency. Solar generation drops precipitously during nocturnal hours and overcast weather, whereas wind power yields fluctuate unpredictably with atmospheric pressure gradients.

To reconcile variable supply with steady municipal and industrial electricity demand, utility operators must deploy grid-scale energy storage. Lithium-ion batteries have established dominance in consumer electronics and electric mobility, yet their suitability for multi-day seasonal electricity storage remains contentious. Lithium extraction incurs severe environmental degradation, and battery cells degrade prematurely under prolonged high-temperature cycling.

Alternative technologies are consequently gathering significant momentum. Pumped-storage hydroelectricity, which exploits surplus electricity to pump water into elevated reservoirs before discharging it through turbines during peak demand, still accounts for over ninety percent of global storage capacity. However, topographical constraints and catastrophic hydrological risks severely restrict its further expansion. Engineers are thus turning toward flow batteries—using vanadium electrolytes that exhibit indefinite cycle life without degradation—and thermal storage systems that store energy in molten salts at temperatures exceeding five hundred degrees Celsius.
""",
                "questions": [
                    {
                        "id": "ar_q1",
                        "prompt": "1. The manufacturing cost of solar panels has risen steeply over the last decade.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "FALSE",
                        "explanation": "Metinde maliyetin yüzde seksenin üzerinde düştüğü (plummeted by more than eighty percent) belirtilmiştir."
                    },
                    {
                        "id": "ar_q2",
                        "prompt": "2. Lithium-ion batteries are universally considered the optimal solution for multi-day seasonal grid storage.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "FALSE",
                        "explanation": "Metinde lityum-iyon pillerin çok günlük mevsimsel depolamadaki yeri 'contentious' (tartışmalı) olarak tanımlanmıştır."
                    },
                    {
                        "id": "ar_q3",
                        "prompt": "3. Pumped-storage hydroelectricity currently generates the vast majority of worldwide stored energy.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "TRUE",
                        "explanation": "Metinde 'accounts for over ninety percent of global storage capacity' ifadesi yer almaktadır."
                    },
                    {
                        "id": "ar_q4",
                        "prompt": "4. Vanadium flow batteries lose half of their energy storage capacity after three years of active use.",
                        "type": "tfng",
                        "options": ["TRUE", "FALSE", "NOT GIVEN"],
                        "answer": "NOT GIVEN",
                        "explanation": "Metinde vanadyum pillerin süresiz döngü ömrüne sahip olduğu söylenmiş ancak 3 yıl içinde kapasite kaybı verisine değinilmemiştir."
                    }
                ]
            }
        },
        "writing": {
            "task_1": {
                "title": "Task 1 (Academic Report - 150 Words)",
                "prompt": """
The pie charts depict the proportion of electricity generated from various energy sources (Coal, Natural Gas, Nuclear, Renewables) in an industrialized nation in 2010 and 2024.

Summarise the information by selecting and reporting the main features, and make comparisons where relevant.
Write at least 150 words.
"""
            },
            "task_2": {
                "title": "Task 2 (Academic Essay - 250 Words)",
                "prompt": """
Some people believe that universities should focus exclusively on providing students with practical vocational knowledge and skills directly applicable to the employment market.
Others argue that the primary purpose of higher education is to pursue academic knowledge for its own sake, regardless of immediate economic utility.

Discuss both views and give your own reasoned opinion.
Write at least 250 words.
"""
            }
        },
        "speaking": {
            "part_1": {
                "title": "Part 1: Studies, Hobbies & Technology",
                "questions": [
                    "What are you currently studying or working on?",
                    "Do you prefer reading printed books or digital content on screens? Why?",
                    "How often do you use public transportation in your hometown?"
                ]
            },
            "part_2": {
                "title": "Part 2: Cue Card (Long Turn)",
                "cue_card": """
Describe an environmental problem that your country or local community is facing.

You should say:
• What the problem is and what caused it
• How it affects ordinary people and local wildlife
• What measures the government or community are taking
And explain whether you believe this environmental issue can be successfully solved in the future.
""",
                "prep_time": 60,
                "speak_time": 120
            },
            "part_3": {
                "title": "Part 3: Environmental Discussion",
                "questions": [
                    "Whose responsibility is it primarily to curb global climate change: governments, corporations, or individual consumers?",
                    "Do you think international environmental agreements are genuinely effective without punitive enforcement mechanisms?",
                    "How can schools better educate children on sustainable living and resource conservation?"
                ]
            }
        }
    }
}
