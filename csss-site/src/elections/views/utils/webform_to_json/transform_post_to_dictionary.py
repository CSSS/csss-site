from querystring_parser import parser


def transform_post_to_dictionary(request):
    """
    transforming the POST request into a workable dictionary

    Keyword Argument
    request -- the django request object

    Return
    dict - the dictionary that can be used to process the user's input
    """
    return parser.parse(request.POST.urlencode())
