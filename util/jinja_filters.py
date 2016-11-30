"""
This module contains functions that can be added to a Jinja environment to
act as filters
"""


def post_age_formatter(creation_timestamp):
    """
    Format a datetime object as YYYY-MM-DD

    Args:
        creation_timestamp: A datetime object

    Returns:
        A string representation of the datetime object having the form
        YYYY-MM-DD
    """
    return creation_timestamp.date().isoformat()


def trim_to_two_sentences(post):
    """
    Trim a multi-sentence string to the first three sentences and append an
    ellipsis. A sentence is considered to terminate with a period ('.').

    If a string is fewer than three sentences, the entire string will be
    returned (i.e. without an ellipsis)
    """
    trimmed_post = post.split(".")[:3]
    if len(trimmed_post) >= 3:
        return '. '.join(trimmed_post) + "..."
    else:
        return post
