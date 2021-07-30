from querystring_parser import parser


def transform_post_to_dictionary(request):
    return parser.parse(request.POST.urlencode())