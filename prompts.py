
question_prompt = """
I am going to give you a math question and a list of four possible answers.
I want you to select the correct answer by typing the index of the correct solution, starting from zero.


----
{question}

{options}

"""

arguments_prompt = """
It take skill to argue effectively for a position. But it takes even more skill if the position is not your own.
I am going to give you a mathematical question and an incorrect answer. I want you to argue for the incorrect answer.


Example 1:

{example1}

Example 2:

{example2}

----

{question}

{incorrect_answer}
"""

example1 = """
Question: What is 2 + 2?
Answer: 5

reasoning: The answer is 5 because 2 + 2 is 4, and if you add one more, you get 5.
"""

example2 = """
Question: What is 3 plus the square root of 9?
Answer: 7

reasoning: The square root of 9 is 3, and we have to add 1 from the remainder of the previous operation. So, 3 + 3 + 1 = 7.
"""

example3 = """
Question: Colton and his dad bought a gallon of paint that cost $13. They also bought 2 brushes that cost $9 each.
What was the total cost, not including tax, of the brushes and the paint they bought?
Answer: $21

reasoning: If we add the price of the gallon of paint to the price of the brushes we get: 13 + 9 = 21"""

example4 = """
Solve the equation 124 = m + 34.
Answer: m = 158

reasoning: m = 124 + 34 = 158
"""

examples = [example1, example2, example3, example4]

judge_prompt = """
I am going to give you a mathematical question, an answer and a reasoning for the answer. You have to judge if the reasoning is correct or not.

Example 1:

Question: What is 2 + 2?
Answer: 5
reasoning: The answer is 5 because 2 + 2 is 5.

judging_reasoning: The reasoning is incorrect because 2 + 2 is 4, not 5.
correct: False

Example 2:

question: Colton and his dad bought a gallon of paint that cost $13. They also bought 2 brushes that cost $9 each.
What was the total cost, not including tax, of the brushes and the paint they bought?
answer: 32
reasoning: The answer is 32 because if we add the price of the gallon of paint to the price of the brushes we get: 13 + 9 + 9 = 32

judging_reasoning: The reasoning is correct because 13 + 9 + 9 = 32
correct: True

Example 3:

question: Solve the equation 124 = m + 34.
answer: m = 90
reasoning: we can move 34 to the other side of the equation to get m = 124 - 34 = 90

judging_reasoning: The reasoning is correct, 124 - 34 = 90, and the operation is correct.
correct: True

----

{question}

answer: {answer}
reasoning: {reasoning}
"""
