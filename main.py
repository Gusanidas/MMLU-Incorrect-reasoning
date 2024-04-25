from datasets import load_dataset
import random
import os
from anthropic import AsyncAnthropic
from openai import OpenAI, AsyncOpenAI
import instructor
import asyncio
from pydantic import BaseModel
from prompts import question_prompt, arguments_prompt, examples, judge_prompt
from dotenv import load_dotenv
import time

load_dotenv()

mmlu = load_dataset('cais/mmlu', "high_school_mathematics", split=['test'])[0]

use_openai = True

if use_openai:
    api_key = os.getenv("OPENAI_API_KEY")
    _client = AsyncOpenAI(api_key=api_key)
    client = instructor.from_openai(_client)
    small_model = "gpt-3.5-turbo"
    big_model = "gpt-4-1106-preview"
    filename = "openai_results.txt"
else:
    # Doesnt seem to work.
    api_key = os.getenv("ANTHROPIC_API_KEY")
    _client = AsyncAnthropic(api_key=api_key)
    client = instructor.from_anthropic(_client)
    
    small_model = "claude-3-haiku-20240307"
    big_model = "claude-3-opus-20240229"
    filename = "anthropic_results.txt"

class MMLU_response(BaseModel):
    reasoning: str
    index: int

class IncorrectReasoning(BaseModel):
    reasoning: str

class JudgingResponse(BaseModel):
    judging_reasoning: str
    correct: bool






def append_question_details(filename, q, incorrect_answer, answer_small, answer_big, example_idx, incorrect_reasoning, judge_response_correct, judge_response_incorrect):
    with open(filename, 'a') as file:
        file.write(f"Question: {q['question']}\n")
        file.write(f"Choices: {q['choices']}\n")
        file.write(f"Correct Answer: {q['choices'][q['answer']]}\n")
        file.write(f"Small Model Answer: {q['choices'][answer_small.index]}\n")
        file.write(f"Small Model Reasoning: {answer_small.reasoning}\n")
        file.write(f"Big Model Answer: {q['choices'][answer_big.index]}\n")
        file.write(f"Big Model Reasoning: {answer_big.reasoning}\n")
        file.write(f"Judge response correct: {judge_response_correct.correct}\n")
        file.write(f"Judge reasoning correct: {judge_response_correct.judging_reasoning}\n")
        file.write("----\n")
        file.write(f"Incorrect Answer chosen: {incorrect_answer}\n")
        file.write(f"Example Index: {example_idx}\n")
        file.write(f"Incorrect Reasoning: {incorrect_reasoning}\n")
        file.write(f"Judge's Reasoning: {judge_response_incorrect.judging_reasoning}\n")
        file.write(f"Judgment Correct: {judge_response_incorrect.correct}\n")
        file.write("----\n\n")
        file.write("************----\n")
        file.write("************----\n\n")



async def process_question(q: dict):
    prompt = question_prompt.format(question=q['question'], options=q['choices'])
    answer_small = await client.chat.completions.create(model=small_model, response_model=MMLU_response, messages=[{"role": "user", "content": prompt}], max_tokens=512)
    answer_big = await client.chat.completions.create(model=big_model, response_model=MMLU_response, messages=[{"role": "user", "content": prompt}], max_tokens=512)
    r = {"big_better": False, "small_correct_judgment": False, "small_incorrect_judgment": False}

    if answer_big.index == q['answer'] and answer_small.index != q['answer']:
        r["big_better"] = True
        judge_p = judge_prompt.format(question=q['question'], answer=answer_big.index, reasoning=answer_big.reasoning)
        judge_response_correct = await client.chat.completions.create(model=small_model, response_model=JudgingResponse, messages=[{"role": "user", "content": judge_p}], max_tokens=512)
        r["small_correct_judgment"] = judge_response_correct.correct
        example_idx = random.sample(range(len(examples)), 2)
        incorrect_answer = q['choices'][(q['answer']+random.randint(1,3))%4]
        arg_prompt = arguments_prompt.format(question=q['question'], example1=examples[example_idx[0]], example2=examples[example_idx[1]], incorrect_answer=incorrect_answer)
        incorrect_reasoning = await client.chat.completions.create(model=big_model, response_model=IncorrectReasoning, messages=[{"role": "user", "content": arg_prompt}], max_tokens=512)
        judge_p = judge_prompt.format(question=q['question'], answer=incorrect_answer, reasoning=incorrect_reasoning.reasoning)
        judge_response_incorrect = await client.chat.completions.create(model=small_model, response_model=JudgingResponse, messages=[{"role": "user", "content": judge_p}], max_tokens=512)
        r["small_incorrect_judgment"] = judge_response_incorrect.correct
        if judge_response_incorrect.correct:
            append_question_details(filename, q, incorrect_answer, answer_small, answer_big, example_idx, incorrect_reasoning.reasoning, judge_response_correct, judge_response_incorrect) 
    return r

async def main():
    tasks = []
    for i, q in enumerate(mmlu):
        if i < 28:
            continue
        tasks.append(asyncio.create_task(process_question(q)))
        if i > 156:
            break
    r = await asyncio.gather(*tasks)
    print(f"Number of times big was correct when small was not: {sum([x['big_better'] for x in r])}")
    print(f"Jugment of the correct reasoning as valid by the small model: {sum([x['small_correct_judgment'] for x in r])}")
    print(f"Jugment of the incorrect reasoning as valid by the small model: {sum([x['small_incorrect_judgment'] for x in r])}")

if __name__ == "__main__":
    t0 = time.time()
    asyncio.run(main())
    print("Done!, time elapsed: ", time.time()-t0)