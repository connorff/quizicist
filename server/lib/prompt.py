from __future__ import annotations
from lib.consts import NUM_QUESTIONS


TEMPLATE = {
    "instruction": "Use the following template for each question:",
    "question": "Question: ",
    "correct": "Correct answer: ",
    "distractor": "Incorrect answer: "
}


class Prompt:
    prompt: str = ""
    num_questions: int = NUM_QUESTIONS


    def __init__(self, prompt="", num_questions=NUM_QUESTIONS):
        self.prompt = prompt
        self.num_questions = num_questions


    def join(self, other: Prompt) -> Prompt:
        return Prompt(self.prompt + other.prompt, self.num_questions)


    def add_text(self, text: str, newlines=1) -> Prompt:
        for _ in range(newlines):
            self.prompt += "\n"

        self.prompt += text
        return self


    def add_introduction(self) -> Prompt:
        intro = "You are a professor creating a challenging multiple-choice quiz for your class. "\
                "The questions you write will test your students' knowledge of abstract concepts from the passage above. "\
                "The questions will be very difficult, cover distinct topics, and not restate simple facts from the passage. "\
                f"The quiz contains {self.num_questions} multiple-choice questions."

        return self.add_text(intro, newlines=2)


    def add_question(self, question: str) -> Prompt:
        return self.add_text(TEMPLATE["question"] + question)

    
    def add_correct(self, correct: str) -> Prompt:
        return self.add_text(TEMPLATE["correct"] + correct)


    def add_distractor(self, distractor: str) -> Prompt:
        return self.add_text(TEMPLATE["distractor"] + distractor)


    def add_template(self) -> Prompt:
        self.add_text(TEMPLATE["instruction"], newlines=2)
        self.add_question("")
        self.add_correct("")
        
        for _ in range(3):
            self.add_distractor("")

        return self


    def add_instructions(self) -> Prompt:
        self.add_text(f"{self.num_questions} multiple-choice questions:", newlines=2)
        return self.add_question("")
