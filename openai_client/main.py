import openai

from config import settings


SYSTEM_TEACHER_PROMPT = """
You're a teacher, which wants to check student's open-ended quizzes. 
Behave yourself friendly but at the same moment make sure students answer fully and only the question, which was given.
Your main goal would be to give scores (in % out of 100% correct) 
for each answer to the given question, and also to explain, why the score is as it is.
Also, you will be given an expected answer for the question - take it into account.
Please answer the same language in which you get the answers.
You will be given the question, expected_answer and user_answer in the format:
Q: {question}
E: {expected_answer}
A: {User_answer}

And you need to answer:
Score: {score}
Explanation: {explanation}
"""

EXAMPLE_USER_PROMPT = """
Q: What is Python?
E: Python is a programming language, which is used for web development, data science, machine learning and much more.
A: Python is the most hated language in the world
"""

EXAMPLE_ASSISTANT_ANSWER = """
Score: 20%
Explanation: Yes, Python is a programming language, but it's not the most hated language in the world. 
And you haven't specified much information about this specific language itself.
"""

TEMPERATURE = 0  # Randomness of the completions


openai.api_key = settings.OPENAI_API_KEY


def get_assistant_answer(
    question: str, expected_answer: str, user_answer: str
) -> tuple[int, str]:
    prompt = f"Q: {question}\n E: {expected_answer}\n A: {user_answer}"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_TEACHER_PROMPT},
            {"role": "user", "content": EXAMPLE_USER_PROMPT},
            {
                "role": "assistant",
                "content": EXAMPLE_ASSISTANT_ANSWER,
            },
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
    )

    message = completion["choices"][0]["message"]["content"]
    score, explanation = message.split("\n")
    score = int(score.split()[1][:-1])
    explanation = explanation[len("Explanation: ") :]

    return score, explanation


if __name__ == "__main__":
    print(
        get_assistant_answer(
            question="What are variables?", answer="Variables are data"
        )
    )
