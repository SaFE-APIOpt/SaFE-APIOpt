
import argparse
import pandas as pd
from openai import OpenAI


API_KEY = " "  # Replace 'API_KEY' with your own key
client = OpenAI(api_key=API_KEY)


# Prompt template
PROMPT_TEMPLATE = """
Definition：
Scenario-aware Functional Equivalent (SaFE) API pair refers to APIs that, regardless of whether their original functionalities are identical, can be employed interchangeably within the same application scenarios to achieve equivalent functionality.
Task Description:
The following content is derived from a SO post concerning the selection and application of  SaFE APIs. It includes the post title, question description, and corresponding answers, which may contain code snippets, references to API documentation, and discussions of specific programming functions or APIs.
Your task is twofold:
（1）Analyze the provided content to identify potential SaFE API pairs based on their functional equivalence and usage context.
（2）Clarify the constraints on test inputs for a SaFE API pair under particular scenarios where the two APIs can be used interchangeably.
（3）Generate test inputs at varying scales that satisfy the corresponding constraints for each potential pair to identify the true SaFe API pair.
Requirements:
1. Potential SaFE API Extraction
(1) Analyze the given text and code snippets, and extract all referenced APIs or functions, clearly providing the complete API name prefixed by its package (e.g., numpy.ravel).
(2) Identify APIs that exhibit functional equivalence under specific usage scenarios. For scenarios where multiple APIs can serve the same functionality, generate all possible two-way combinations, since any two of them may constitute a SaFE API pair. Each combination should be treated as a candidate SaFE API pair.
2. Generation of the scenario constraints for SaFE API pairs
For each identified SaFE API pair, generate precise usage constraints that specify the conditions under which the two APIs can be used interchangeably. 
The constraints should cover:
（1）The required input data types and shapes that both APIs are able to process;
（2）Any preconditions or semantic constraints that must hold for the two APIs to exhibit equivalent behavior;
3. Test Input Generation for SaFE API Pairs
Based on the above output, provide Python code to generate evaluation inputs at four scales, with each dimension sized 10, 100, 1,000, and 10,000. The elements must be randomly generated and satisfy the input type and constraints defined in points (1) and (2).

Example Context:
Title: correct and efficient way to flatten array in numpy in python?
I have:
a = array([[1,2,3],[4,5,6]])
and I'd like to flatten it, joining the two inner lists into one flat array entry. I can do:
array(list(flatten(a)))
but that seems inefficient due to the list cast (I want to end up with an array and not a generator.)
Also, how can this be generalized to an array like this:
b = array([[[1,2,3],[4,5,6]], [[10,11,12],[13,14,15]]])
where the result should be:
b = array([[1,2,3,4,5,6],
           [10,11,12,13,14,15]])
are there builtin/efficient numpy/scipy operators for this? thanks.

Answer1:You might need to check out numpy.flatten and numpy.ravel, both return a 1-d array from an n-d array.
Furthermore, if you're not going to modify the returned 1-d array, I suggest you use numpy.ravel, since it doesn't make a copy of the array, but just return a view of the array, which is much faster than numpy.flatten.
>>>a = np.arange(10000).reshape((100,100))
>>>%timeit a.flatten()
100000 loops, best of 3: 4.02 µs per loop
>>>%timeit a.ravel()
1000000 loops, best of 3: 412 ns per loop

Answer2:You can use the reshape method.

>>> import numpy
>>> b = numpy.array([[[1,2,3],[4,5,6]], [[10,11,12],[13,14,15]]])
>>> b.reshape([2, 6])
array([[ 1,  2,  3,  4,  5,  6],
       [10, 11, 12, 13, 14, 15]])
       
Example Output:
After analysis of the above SO post content, three SaFE API pairs are identified:
numpy.ndarray.flatten vs. numpy.ndarray.ravel
numpy.ndarray.reshape vs. numpy.ndarray.ravel
numpy.ndarray.flatten vs. numpy.ndarray.reshape  

"""

def main():
    parser = argparse.ArgumentParser(
        description="Read an Excel of SO answers and generate performance case via GPT."
    )
    parser.add_argument('input_file', help='Excel file with "answers_text" and "code_blocks" columns')
    parser.add_argument('--output', default='generated_output.xlsx',
                        help='Filename for the output Excel (default: generated_output.xlsx)')
    args = parser.parse_args()

    df = pd.read_excel(args.input_file)
    df["generated_code"] = None
    total = len(df)

    for idx, row in df.iterrows():
        # Safely coerce NaN or non-string to empty string
        raw_text = row.get("answers_text")
        text_part = raw_text if isinstance(raw_text, str) else ""

        raw_code = row.get("code_blocks")
        code_part = raw_code if isinstance(raw_code, str) else ""

        combined = (
            "### Answer Text ###\n" +
            text_part +
            "\n\n### Code Snippets ###\n" +
            code_part
        )

        messages = [
            {"role": "system", "content": "You are a professional AI assistant, adept at analyzing text and code and generating test cases."},
            {"role": "user", "content": combined},
            {"role": "user", "content": PROMPT_TEMPLATE}
        ]

        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.0,
                max_tokens=2000
            )
            df.at[idx, "generated_code"] = resp.choices[0].message.content
            print(f"[{idx+1}/{total}] Generated successfully.")
        except Exception as e:
            print(f"[{idx+1}/{total}] Error: {e}")
            df.at[idx, "generated_code"] = f"Error: {e}"

    df.to_excel(args.output, index=False)
    print(f"Done! Results saved to {args.output}")


if __name__ == "__main__":
    main()