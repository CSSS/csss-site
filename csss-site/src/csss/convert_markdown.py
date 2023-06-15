import markdown


def markdown_message(message):
    """
    Marks down the given message using the markdown module

    Keyword Argument
    message -- the message to mark down

    Return
    message - the marked down message
    """
    return markdown.markdown(
        message, extensions=[
            'sane_lists', 'markdown_link_attr_modifier'
        ],
        extension_configs={
            'markdown_link_attr_modifier': {
                'new_tab': 'on',
            },
        }
    )
