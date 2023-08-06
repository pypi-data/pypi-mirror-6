if __name__ == '__main__':

    import sys
    import os.path
    import tvd
    from argparse import ArgumentParser, HelpFormatter
    main_parser = ArgumentParser(
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        version=None,
        parents=[],
        formatter_class=HelpFormatter,
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True
    )

    description = 'Select which series to process (defaults to all).'
    series_parser = main_parser.add_argument_group(description)

    for series_name, series_class in tvd.get_series().iteritems():

        series_parser.add_argument(
            '--{name}'.format(name=series_name),
            action='append_const',
            dest='series',
            const=series_class,
            default=[],
            help='Process series "{name}"'.format(name=series_name)
        )

    description = 'TVD root directory'
    main_parser.add_argument(
        'tvd_dir', type=str, help=description
    )

    try:
        args = main_parser.parse_args()
    except Exception, e:
        sys.exit(e)

    if not args.series:
        series = [
            series_class
            for _, series_class in tvd.get_series().iteritems()
        ]

    tvd_dir = args.tvd_dir

    for series_class in series:

        plugin = series_class()

        # create series directory if it does not exist
        series_dir = os.path.join(tvd_dir, plugin.series)

        # create www directory if it does not exist
        www_dir = os.path.join(series_dir, 'www')



