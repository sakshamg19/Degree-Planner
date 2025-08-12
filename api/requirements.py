
"""
Degree requirement rules data for L&S (BS) degree + CS major
Conventions:
- Course codes are upper-cased and trimmed by the evaluator.
- Cross-listings are normalized using ALIASES.
- Section types:
    - ALL_OF: must complete all listed "items" (each item has code, credits)
    - ONE_OF: must complete ONE of "options"
        * each option can be:
            - {"type": "COURSE", "code": "...", "credits": n}
            - {"type": "ALL_OF", "items": [COURSE,...]}
    - N_OF: must complete N from "items"
- credits_range fields are informational (not enforced in MVP).
"""

# --- Cross-listing normalization (expand as needed) ---
ALIASES = {
    "COMP SCI/ECE 354": "COMP SCI 354",
    "COMP SCI/ECE 252": "COMP SCI 252",
    "STAT/MATH 309": "STAT 309",
    "COMP SCI/I SY E/MATH 425": "COMP SCI 425",
    "COMP SCI/ECE/I SY E 524": "COMP SCI 524",
    "COMP SCI/I SY E/MATH/STAT 525": "COMP SCI 525",
    "COMP SCI/DS 579": "COMP SCI 579",
    "COMP SCI/ECE/ME 539": "COMP SCI 539",
    "COMP SCI/ECE 533": "COMP SCI 533",
    "COMP SCI/ECE 552": "COMP SCI 552",
    "COMP SCI/STAT 471": "COMP SCI 471",
    "COMP SCI/MATH/STAT 475": "COMP SCI 475",
}

# -----------------------------
# DEGREE (L&S BS) 
# -----------------------------
DEGREE_REQUIREMENTS = {
    "L&S_BS": {
        "id": "L&S_BS",
        # Total credits to graduate 
        "total_degree_credits": 120,

        # University Gen Ed (as labels for MVP; not auto-checked yet)
        "gen_ed": {
            "Humanities": 6,
            "Natural Science": "4-6",      # usually 4–6 with lab
            "Social Studies": 3,
            "Communication A": 3,
            "Communication B": 3,
            "Ethnic Studies": 3,
            "Quantitative Reasoning A": 3,
            "Quantitative Reasoning B": 3
        },

        # L&S BS-specific high-level items (labels now; you can encode rules later)
        "ls_specific": {
            "Mathematics": "Two 3+ credit courses at Intermediate/Advanced (MATH/COMP SCI/STAT)",
            "Language": "Third unit of a language other than English",
            "LS_Breadth": {
                "Humanities": 12,
                "Social Science": 12,
                "Natural Science": 12  # includes Bio + Physical split in the Guide
            },
            "L&S Coursework": "At least 108 credits",
            "Depth Intermediate/Adv": "At least 60 credits at Intermediate/Adv level",
            "UW-Madison Experience": "30 cr in residence overall + 30 cr after 86th",
            "Quality of Work": "2.000 overall; 2.000 at Intermediate/Adv"
        }
    }
}

# -----------------------------
# CS MAJOR (L&S)
# -----------------------------
MAJOR_REQUIREMENTS = {
    "CS_LS": {
        "id": "Computer Science (L&S)",
        "college": "L&S_BS",
        "total_major_credits": 48,

        "sections": [
            # Basic Computer Sciences (ALL_OF)
            {
                "id": "basic_cs",
                "title": "Basic Computer Sciences",
                "type": "ALL_OF",
                "items": [
                    {"code": "MATH/COMP SCI 240", "credits": 3},
                    {"code": "COMP SCI/E C E 252", "credits": 3},
                    {"code": "COMP SCI 300", "credits": 3},
                    {"code": "COMP SCI/E C E 354", "credits": 3},
                    {"code": "COMP SCI 400", "credits": 3}
                ],
                "credits_total": 15
            },

            # Basic Calculus (ONE_OF) – sequences
            {
                "id": "basic_calculus",
                "title": "Basic Calculus (sequence)",
                "type": "ONE_OF",
                "options": [
                    { "type": "ALL_OF", "items": [
                        {"code": "MATH 221", "credits": 5},
                        {"code": "MATH 222", "credits": 4}
                    ]},
                    { "type": "ALL_OF", "items": [
                        {"code": "MATH 171", "credits": 5},
                        {"code": "MATH 217", "credits": 4},
                        {"code": "MATH 222", "credits": 4}
                    ]}
                ],
                "credits_range": [9, 14]
            },

            # Additional Mathematics – Linear Algebra (ONE_OF)
            {
                "id": "linear_algebra",
                "title": "Additional Mathematics (Linear Algebra)",
                "type": "ONE_OF",
                "options": [
                    {"type": "COURSE", "code": "MATH 320", "credits": 3},
                    {"type": "COURSE", "code": "MATH 340", "credits": 3},
                    {"type": "COURSE", "code": "MATH 345", "credits": 4},
                    {"type": "COURSE", "code": "MATH 341", "credits": 3},
                    {"type": "COURSE", "code": "MATH 375", "credits": 5}
                ],
                "credits_min": 3
            },

            # Probability or Statistics (ONE_OF)
            {
                "id": "prob_or_stats",
                "title": "Probability or Statistics",
                "type": "ONE_OF",
                "options": [
                    {"type": "COURSE", "code": "STAT/MATH 309", "credits": 3},
                    {"type": "COURSE", "code": "STAT 311", "credits": 3},
                    {"type": "COURSE", "code": "STAT 324", "credits": 3},
                    {"type": "COURSE", "code": "MATH 331", "credits": 3},
                    {"type": "COURSE", "code": "STAT 333", "credits": 3},
                    {"type": "COURSE", "code": "STAT 340", "credits": 4},
                    {"type": "COURSE", "code": "STAT 371", "credits": 3},
                    {"type": "COURSE", "code": "STAT/MATH 431", "credits": 3},
                    {"type": "COURSE", "code": "MATH 531", "credits": 3}
                ],
                "credits_min": 3
            },

            # Advanced CS – Theory (ONE_OF)
            {
                "id": "theory",
                "title": "Advanced CS: Theory of Computer Science",
                "type": "ONE_OF",
                "options": [
                    {"type": "COURSE", "code": "COMP SCI 577", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 520", "credits": 3}
                ],
                "credits_min": 3
            },

            # Advanced CS – Software & Hardware (N_OF pick 2)
            {
                "id": "software_hardware",
                "title": "Advanced CS: Software & Hardware (pick two)",
                "type": "N_OF",
                "n": 2,
                "items": [
                    {"code": "COMP SCI 407", "credits": 3},
                    {"code": "COMP SCI/E C E 506", "credits": 3},
                    {"code": "COMP SCI 536", "credits": 3},
                    {"code": "COMP SCI 538", "credits": 3},
                    {"code": "COMP SCI 537", "credits": 3},
                    {"code": "COMP SCI 542", "credits": 3},
                    {"code": "COMP SCI 544", "credits": 3},
                    {"code": "COMP SCI/E C E 552", "credits": 3},
                    {"code": "COMP SCI 557", "credits": 3},
                    {"code": "COMP SCI 564", "credits": 3},
                    {"code": "COMP SCI 640", "credits": 3},
                    {"code": "COMP SCI 642", "credits": 3}
                ],
                "credits_range": [6, 8]
            },

            # Applications (ONE_OF)
            {
                "id": "applications",
                "title": "Applications (pick one)",
                "type": "ONE_OF",
                "options": [
                    {"type": "COURSE", "code": "COMP SCI 412", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI/I SY E/MATH 425", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI/MATH 513", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI/MATH 514", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI/E C E/I SY E 524", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI/I SY E/MATH/STAT 525", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 534", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 540", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 541", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 559", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 565", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 566", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 570", "credits": 3},
                    {"type": "COURSE", "code": "COMP SCI 571", "credits": 3}
                ],
                "credits_min": 3
            },

            # Electives (N_OF pick 2) – long list trimmed slightly for MVP
            {
                "id": "electives",
                "title": "Electives (pick two)",
                "type": "N_OF",
                "n": 2,
                "items": [
                    {"code": "COMP SCI 407", "credits": 3},
                    {"code": "COMP SCI 412", "credits": 3},
                    {"code": "COMP SCI/E C E/MATH 435", "credits": 3},
                    {"code": "COMP SCI/STAT 471", "credits": 3},
                    {"code": "COMP SCI/MATH/STAT 475", "credits": 3},
                    {"code": "COMP SCI/E C E 506", "credits": 3},
                    {"code": "COMP SCI/M E/E C E 532", "credits": 3},
                    {"code": "COMP SCI/E C E 533", "credits": 3},
                    {"code": "COMP SCI 534", "credits": 3},
                    {"code": "COMP SCI 536", "credits": 3},
                    {"code": "COMP SCI 537", "credits": 3},
                    {"code": "COMP SCI 538", "credits": 3},
                    {"code": "COMP SCI/E C E/M E 539", "credits": 3},
                    {"code": "COMP SCI 540", "credits": 3},
                    {"code": "COMP SCI 541", "credits": 3},
                    {"code": "COMP SCI 542", "credits": 3},
                    {"code": "COMP SCI 544", "credits": 3},
                    {"code": "COMP SCI/E C E 552", "credits": 3},
                    {"code": "COMP SCI 557", "credits": 3},
                    {"code": "COMP SCI 564", "credits": 3},
                    {"code": "COMP SCI 565", "credits": 3},
                    {"code": "COMP SCI 566", "credits": 3},
                    {"code": "COMP SCI 579", "credits": 3},
                    {"code": "COMP SCI 639", "credits": 3},
                    {"code": "COMP SCI 640", "credits": 3},
                    {"code": "COMP SCI 642", "credits": 3}
                ],
                "credits_range": [6, 8]
            }
        ]
    }
}
