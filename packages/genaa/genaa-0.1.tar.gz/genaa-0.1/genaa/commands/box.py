import sys

from genaa.box import Box, style_mapping


def apply_arguments(parser):
    parser.add_argument('-t', '--text', dest='text',
                        help='Passing text by argument into box')
    parser.add_argument('-W', '--width', dest='width', type=int)
    parser.add_argument('-H', '--height', dest='height', type=int)
    parser.add_argument('-s', '--style', dest='style',
                        default='ascii', choices=style_mapping.keys())
    parser.add_argument('-a', '--align', choices=('left', 'center', 'right'),
                        default='left', dest='align')
    parser.set_defaults(func=run)
    return parser


def run(opt):
    if getattr(opt, 'text'):
        text = opt.text
    else:
        text = sys.stdin.read()

    box = Box(style_mapping[opt.style],
              width=opt.width, height=opt.height,
              align=opt.align, text=text)

    return box.render()
