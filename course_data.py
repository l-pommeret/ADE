"""
Module contenant les données des cours du Master LOGOS.
"""

# Structure des cours par semestre
COURSES = {
    "semestre1": {
        "title": "SEMESTRE 1 (30 ECTS)",
        "description": """The student must choose at least one course from each block with a total of at least 30 ECTS credits.""",
        "blocks": {
            "A": {
                "title": "Philosophy of Science block",
                "description": "1 UE of 6 ECTS :",
                "courses": [
                    {
                        "id": "s1_a1",
                        "title": "Introduction to the philosophy of science",
                        "ects": 6,
                        "description": "Introduction to the philosophy of science"
                    }
                ]
            },
            "B": {
                "title": "Linguistics block",
                "description": "Choice of 1 or 2 UE of 6 ECTS each among:",
                "courses": [
                    {
                        "id": "s1_b1",
                        "title": "Theoretical syntax",
                        "ects": 6,
                        "description": "Theoretical syntax"
                    },
                    {
                        "id": "s1_b2",
                        "title": "Introduction to syntax",
                        "ects": 6,
                        "description": "Introduction to syntax"
                    },
                    {
                        "id": "s1_b3",
                        "title": "Semantic analysis",
                        "ects": 6,
                        "description": "Semantic analysis"
                    },
                    {
                        "id": "s1_b4",
                        "title": "Language and its interfaces",
                        "ects": 6,
                        "description": "Language and its interfaces"
                    }
                ]
            },
            "C": {
                "title": "Logic block",
                "description": "Choice of 1 UE for 12 ECTS or 2 UE for 9 ECTS among:",
                "courses": [
                    {
                        "id": "s1_c1",
                        "title": "Logic",
                        "ects": 9,
                        "description": "Logic"
                    },
                    {
                        "id": "s1_c2",
                        "title": "Logic + Algorithmics",
                        "ects": 12,
                        "description": "This UE corresponds to two courses: Logic et Algorithms"
                    },
                    {
                        "id": "s1_c3",
                        "title": "Algorithms Complexity",
                        "ects": 9,
                        "description": "This UE corresponds to two courses: Logic and Complexity."
                    },
                    {
                        "id": "s1_c4",
                        "title": "Algorithms and Information Theory",
                        "ects": 9,
                        "description": "This UE corresponds to two courses: Algorithms and Information Theory."
                    }
                ]
            }
        },
        "rules": [
            {
                "min_courses": 3,
                "min_ects": 30,
                "block_requirements": {
                    "A": 1,
                    "B": 1,
                    "C": 1
                }
            }
        ]
    },
    "semestre2": {
        "title": "SEMESTRE 2 (30 ECTS)",
        "description": "The student needs to choose 5 UEs (courses) for 6 ECTS (credits) each (at least one UE in each of the three blocks).",
        "blocks": {
            "A": {
                "title": "Philosophy of Science block",
                "description": "Choice of 1 or 2 UEs of 6 ECTS each from:",
                "courses": [
                    {
                        "id": "s2_a1",
                        "title": "Philosophy of mathematics",
                        "ects": 6,
                        "description": "Philosophy of mathematics"
                    },
                    {
                        "id": "s2_a2",
                        "title": "Mathematics for non-specialists",
                        "ects": 6,
                        "description": "Mathematics for non-specialists"
                    }
                ]
            },
            "B": {
                "title": "Linguistics block",
                "description": "Choice of 1 or 2 courses of 6 ECTS each from:",
                "courses": [
                    {
                        "id": "s2_b1",
                        "title": "Advanced theoretical syntax",
                        "ects": 6,
                        "description": "Advanced theoretical syntax"
                    },
                    {
                        "id": "s2_b2",
                        "title": "Advanced experimental syntax",
                        "ects": 6,
                        "description": "Advanced experimental syntax"
                    },
                    {
                        "id": "s2_b3",
                        "title": "Syntax, semantics, discourse 2",
                        "ects": 6,
                        "description": "Syntax, semantics, discourse 2"
                    },
                    {
                        "id": "s2_b4",
                        "title": "Advanced semantics pragmatics",
                        "ects": 6,
                        "description": "Advanced semantics pragmatics"
                    },
                    {
                        "id": "s2_b5",
                        "title": "Machine learning for NLP1",
                        "ects": 6,
                        "description": "Machine learning for NLP1"
                    },
                    {
                        "id": "s2_b6",
                        "title": "Computational semantics",
                        "ects": 6,
                        "description": "Computational semantics"
                    }
                ]
            },
            "C": {
                "title": "Logic and Computer Science block",
                "description": "Choice of 1 or 2 courses of 6 ECTS from among:",
                "courses": [
                    {
                        "id": "s2_c1",
                        "title": "Incompleteness and undecidability",
                        "ects": 6,
                        "description": "Incompleteness and undecidability"
                    },
                    {
                        "id": "s2_c2",
                        "title": "Set theory",
                        "ects": 6,
                        "description": "Set theory"
                    },
                    {
                        "id": "s2_c3",
                        "title": "Fundamental statistics",
                        "ects": 6,
                        "description": "Fundamental statistics"
                    },
                    {
                        "id": "s2_c4",
                        "title": "Data analysis",
                        "ects": 6,
                        "description": "Data analysis"
                    },
                    {
                        "id": "s2_c5",
                        "title": "Big Data technologies",
                        "ects": 6,
                        "description": "Big Data technologies"
                    }
                ]
            }
        },
        "rules": [
            {
                "min_courses": 5,
                "min_ects": 30,
                "block_requirements": {
                    "A": 1,
                    "B": 1,
                    "C": 1
                }
            }
        ]
    },
    "semestre3": {
        "title": "SEMESTRE 3 (30 ECTS)",
        "description": """The student must choose:
either 5 UEs (courses) for 6 ECTS (credits), or 3 UEs (courses) for 6 ECTS (credits) + 1 UE (course) for 12 ECTS (credits), and in any case at least one UE (course) in each of the four blocks.""",
        "blocks": {
            "A": {
                "title": "Philosophy of Science block",
                "description": "Choice of 1 or 2 courses of 6 ECTS each among :",
                "courses": [
                    {
                        "id": "s3_a1",
                        "title": "Philosophy of knowledge",
                        "ects": 6,
                        "description": "Philosophy of knowledge"
                    },
                    {
                        "id": "s3_a2",
                        "title": "History of linguistic theories",
                        "ects": 6,
                        "description": "History of linguistic theories"
                    }
                ]
            },
            "B": {
                "title": "Linguistics block",
                "description": "Choice of 1 or 2 courses of 6 ECTS each from:",
                "courses": [
                    {
                        "id": "s3_b1",
                        "title": "Discourse and dialogue",
                        "ects": 6,
                        "description": "Discourse and dialogue"
                    },
                    {
                        "id": "s3_b2",
                        "title": "Semantics and pragmatics",
                        "ects": 6,
                        "description": "Semantics and pragmatics"
                    },
                    {
                        "id": "s3_b3",
                        "title": "Machine learning for NLP 2",
                        "ects": 6,
                        "description": "Machine learning for NLP 2"
                    }
                ]
            },
            "C": {
                "title": "Logic block",
                "description": "Choice of 1 or 2 courses of 6 or 12 ECTS each from:",
                "courses": [
                    {
                        "id": "s3_c1",
                        "title": "Model theory",
                        "ects": 6,
                        "description": "Model theory"
                    },
                    {
                        "id": "s3_c2",
                        "title": "Set theory",
                        "ects": 6,
                        "description": "Set theory"
                    },
                    {
                        "id": "s3_c3",
                        "title": "Proof theory",
                        "ects": 6,
                        "description": "Proof theory"
                    },
                    {
                        "id": "s3_c4",
                        "title": "Computability and incompleteness",
                        "ects": 12,
                        "description": "Computability and incompleteness"
                    },
                    {
                        "id": "s3_c5",
                        "title": "Category theory",
                        "ects": 6,
                        "description": "Category theory"
                    }
                ]
            },
            "D": {
                "title": "Computer Science block",
                "description": "Choice of 1 or 2 UE of 6 or 12 ECTS each among:",
                "courses": [
                    {
                        "id": "s3_d1",
                        "title": "Natural language processing",
                        "ects": 6,
                        "description": "Natural language processing"
                    },
                    {
                        "id": "s3_d2",
                        "title": "Machine Learning",
                        "ects": 12,
                        "description": "Machine Learning"
                    },
                    {
                        "id": "s3_d3",
                        "title": "Randomized Complexity",
                        "ects": 6,
                        "description": "Randomized Complexity"
                    },
                    {
                        "id": "s3_d4",
                        "title": "Introduction to Artificial Intelligence and Game Theory",
                        "ects": 6,
                        "description": "Introduction to Artificial Intelligence and Game Theory"
                    },
                    {
                        "id": "s3_d5",
                        "title": "Functional programming and formal proof in COQ",
                        "ects": 6,
                        "description": "Functional programming and formal proof in COQ"
                    },
                    {
                        "id": "s3_d6",
                        "title": "Theories of computation",
                        "ects": 6,
                        "description": "Theories of computation"
                    }
                ]
            }
        },
        "rules": [
            {
                "min_courses": 5,
                "min_ects": 30,
                "block_requirements": {
                    "A": 1,
                    "B": 1,
                    "C": 1,
                    "D": 1
                }
            },
            {
                "min_courses": 4,
                "min_ects": 30,
                "block_requirements": {
                    "A": 1,
                    "B": 1,
                    "C": 1,
                    "D": 1
                },
                "special": "One course of 12 ECTS must be selected"
            }
        ]
    },
    "semestre4": {
        "title": "SEMESTRE 4 (30 ECTS)",
        "description": """This semester is composed of:
either 2 UEs (courses) of 6 ECTS (credits) each (belonging to two different blocks) and the writing of a dissertation counting for 18 ECTS (credits) ("the classical itinerary");
or an internship of at least four months counting for 30 ECTS ("the internship itinerary").""",
        "blocks": {
            "A": {
                "title": "Philosophy of Science block",
                "description": "Choice of 1 UE of 6 ECTS among:",
                "courses": [
                    {
                        "id": "s4_a1",
                        "title": "Philosophy of mathematics",
                        "ects": 6,
                        "description": "Philosophy of mathematics"
                    },
                    {
                        "id": "s4_a2",
                        "title": "Mathematics for non-specialists",
                        "ects": 6,
                        "description": "Mathematics for non-specialists"
                    }
                ]
            },
            "B": {
                "title": "Linguistics block",
                "description": "Choice of 1 UE of 6 ECTS among:",
                "courses": [
                    {
                        "id": "s4_b1",
                        "title": "Advanced theoretical syntax",
                        "ects": 6,
                        "description": "Advanced theoretical syntax"
                    },
                    {
                        "id": "s4_b2",
                        "title": "Advanced experimental syntax",
                        "ects": 6,
                        "description": "Advanced experimental syntax"
                    },
                    {
                        "id": "s4_b3",
                        "title": "Syntax, semantics, discourse 2",
                        "ects": 6,
                        "description": "Syntax, semantics, discourse 2"
                    },
                    {
                        "id": "s4_b4",
                        "title": "Advanced semantics pragmatics",
                        "ects": 6,
                        "description": "Advanced semantics pragmatics"
                    }
                ]
            },
            "C": {
                "title": "Logic block",
                "description": "Choice of 1 UE of 6 ECTS among:",
                "courses": [
                    {
                        "id": "s4_c1",
                        "title": "Set theory: classical tools",
                        "ects": 6,
                        "description": "Set theory: classical tools"
                    },
                    {
                        "id": "s4_c2",
                        "title": "Model theory: classical tools",
                        "ects": 6,
                        "description": "Model theory: classical tools"
                    },
                    {
                        "id": "s4_c3",
                        "title": "Proof-programs: classical tools",
                        "ects": 6,
                        "description": "Proof-programs: classical tools"
                    },
                    {
                        "id": "s4_c4",
                        "title": "Calculability: classical tools",
                        "ects": 6,
                        "description": "Calculability: classical tools"
                    }
                ]
            },
            "D": {
                "title": "Computer Science block",
                "description": "Choice of 1 UE of 6 ECTS among:",
                "courses": [
                    {
                        "id": "s4_d1",
                        "title": "Algorithms for massive data",
                        "ects": 6,
                        "description": "Algorithms for massive data"
                    },
                    {
                        "id": "s4_d2",
                        "title": "Deep Learning",
                        "ects": 6,
                        "description": "Deep Learning"
                    },
                    {
                        "id": "s4_d3",
                        "title": "Logic, descriptive complexity and database theory",
                        "ects": 6,
                        "description": "Logic, descriptive complexity and database theory"
                    }
                ]
            },
            "E": {
                "title": "Thesis or Internship",
                "description": "Choice of:",
                "courses": [
                    {
                        "id": "s4_e1",
                        "title": "Thesis",
                        "ects": 18,
                        "description": "Writing of a dissertation",
                        "requires_info": True,
                        "additional_fields": [
                            {
                                "name": "thesis_title",
                                "label": "Titre du mémoire",
                                "required": True
                            },
                            {
                                "name": "thesis_subject",
                                "label": "Sujet/Description",
                                "required": True
                            },
                            {
                                "name": "thesis_supervisor",
                                "label": "Directeur(s) de mémoire",
                                "required": True
                            }
                        ]
                    },
                    {
                        "id": "s4_e2",
                        "title": "Internship",
                        "ects": 30,
                        "description": "Internship of at least four months",
                        "requires_info": True,
                        "additional_fields": [
                            {
                                "name": "internship_location",
                                "label": "Lieu du stage",
                                "required": True
                            },
                            {
                                "name": "internship_subject",
                                "label": "Sujet du stage",
                                "required": True
                            },
                            {
                                "name": "internship_supervisor",
                                "label": "Directeur(s) de stage",
                                "required": True
                            }
                        ]
                    }
                ]
            }
        },
        "rules": [
            {
                "min_courses": 3,
                "min_ects": 30,
                "block_requirements": {
                    "A": 1,
                    "B": 1,
                    "E": 1
                },
                "note": "Choose Thesis for classical itinerary (plus courses from 2 different blocks)"
            },
            {
                "min_courses": 1,
                "min_ects": 30,
                "block_requirements": {
                    "E": 1
                },
                "note": "Choose Internship for internship itinerary"
            }
        ]
    }
}

# Sample user data
USERS = {
    "user1": {
        "username": "user1",
        "password": "password1",
        "email": "user1@example.com",
        "name": "User One",
        "selected_courses": {
            "semestre1": [],
            "semestre2": [],
            "semestre3": [],
            "semestre4": []
        }
    }
}