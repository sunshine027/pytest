def parse_argument_for_pytest(args, adict):
    if args.find('-c') != -1:
        if args.find('-d') == -1:
            args_list = args.split('-c')
            case_profile = args_list[1].strip()
            adict.setdefault('runtype', 0)
            adict.setdefault('testcfg', case_profile)
    elif args.find('-s') != -1:
        if args.find('-d') == -1:
            args_list = args.split('-s')
            suite_profile = args_list[1].strip()
            adict.setdefault('runtype', 1)
            adict.setdefault('testcfg', suite_profile)
    elif args.find('-e') != -1:
        if args.find('-d') == -1:
            args_list = args.split('-e')
            execution_profile = args_list[1].strip()
            adict.setdefault('runtype', 2)
            adict.setdefault('testcfg', execution_profile)
            
def parse_argument_for_setup(args, adict):
    if args.find('-e') != -1:
        if args.find('-d') == -1:
            args_list = args.split('-e')
            setup_profile = args_list[1].strip()
            adict.setdefault('setupcfg', setup_profile)
