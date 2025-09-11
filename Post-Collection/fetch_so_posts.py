
import argparse
import requests
import pandas as pd

DEFAULT_TAG = 'python'

def fetch_so_posts_advanced(query, tags, pagesize=100, max_pages=10, site='stackoverflow'):
    """
    Fetch posts from StackOverflow matching a query and tags.

    """
    base_url = "https://api.stackexchange.com/2.3/search/advanced"
    all_posts = []

    for page in range(1, max_pages + 1):
        params = {
            'q': query,
            'tagged': tags,
            'site': site,
            'pagesize': pagesize,
            'page': page,
            'order': 'desc',
            'sort': 'relevance',
            'key': ' '  # Replace 'key' with your own key

        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Request failed with status code: {response.status_code}")
            break

        data = response.json()
        for item in data.get('items', []):
            post = {
                'title': item.get('title'),
                'creation_date': pd.to_datetime(item['creation_date'], unit='s'),
                'score': item['score'],
                'tags': ','.join(item['tags']),
                'link': item['link']
            }
            all_posts.append(post)

        if not data.get('has_more', False):
            break

    return pd.DataFrame(all_posts)


def main():
    """
    Command-line interface for fetching StackOverflow posts.
    Usage:
        python fetch_so_posts.py.py <query> <tag>
    Example:
        python fetch_so_posts.py.py fast torch
        → searches for query="fast", tags="python;torch"
    """
    parser = argparse.ArgumentParser(
        description="Fetch StackOverflow posts by keyword and a single tag (python is added by default)."
    )
    parser.add_argument('query', help='Search keyword for title and content')
    parser.add_argument(
        'tag',
        help='A single additional tag to filter posts; "python" is added automatically'
    )
    parser.add_argument(
        '--pagesize',
        type=int,
        default=50,
        help='Number of posts per page (default: 50)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=2,
        help='Maximum number of pages to fetch (default: 2)'
    )
    args = parser.parse_args()

    # build the full tag string by prepending the default tag
    tag_string = f"{DEFAULT_TAG};{args.tag}"

    # fetch matching posts
    df = fetch_so_posts_advanced(
        query=args.query,
        tags=tag_string,
        pagesize=args.pagesize,
        max_pages=args.max_pages
    )

    # show top results
    print(df.head())

    # save to Excel
    safe_tag = args.tag.replace(';', '_')
    output_file = f"{safe_tag}_{args.query}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")


if __name__ == '__main__':
    main()
