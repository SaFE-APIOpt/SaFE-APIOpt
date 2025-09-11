
import time
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup

def fetch_answers_content(url):
    """
    Fetch all answers (text and code) from a StackOverflow question page.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        answers = soup.select('.answer .js-post-body')
        all_texts = []
        all_codes = []

        for ans in answers:
            # extract the answer text
            text = ans.get_text(separator="\n", strip=True)
            all_texts.append(text)

            # extract any code blocks
            code_snippets = ans.select('pre code')
            codes = [code.get_text(separator="\n", strip=True) for code in code_snippets]
            all_codes.append("\n\n".join(codes))

        combined_text = "\n\n---\n\n".join(all_texts)
        combined_codes = "\n\n---\n\n".join(all_codes)
        return combined_text, combined_codes

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None, None


def main():
    """
    Command-line interface for crawling StackOverflow answers.

    Usage:
        python so_answer_crawler.py <input_excel>
    Example:
        python so_answer_crawler.py torch_fast.xlsx
    """
    parser = argparse.ArgumentParser(
        description="Read an Excel file of StackOverflow links and fetch all answer text & code."
    )
    parser.add_argument(
        'input_file',
        help='Path to the input Excel file (must have "title" and "link" columns)'
    )
    parser.add_argument(
        '--output',
        default='post_answer.xlsx',
        help='Filename for the output Excel (default: post_answer.xlsx)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Seconds to wait between requests (default: 0.5)'
    )
    args = parser.parse_args()

    # Read the Excel with title & link columns
    df = pd.read_excel(args.input_file)

    results = []
    total = len(df)
    for idx, row in df.iterrows():
        title = row['title']
        url = row['link']
        print(f"Fetching answers ({idx+1}/{total}): {title}")

        answers_text, code_text = fetch_answers_content(url)
        results.append({
            'title': title,
            'link': url,
            'answers_text': answers_text,
            'code_blocks': code_text
        })

        time.sleep(args.delay)

    # Save to Excel
    output_df = pd.DataFrame(results)
    output_df.to_excel(args.output, index=False)
    print(f"Done! Saved results to {args.output}")


if __name__ == '__main__':
    main()
