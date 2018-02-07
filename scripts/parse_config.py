import tempfile
import ConfigParser

def get_val(config, sec, opt):
    """
    get value from a ini file given the section and option
    the priority here is int, float, boolean and finally string
    """
    try:
        val = config.getint(sec, opt)
    except ValueError:
        try:
            val = config.getfloat(sec, opt)
        except ValueError:
            try:
                val = config.getboolean(sec, opt)
            except ValueError:
                val = config.get(sec, opt)  # shouldn't have any exceptions here..
    return val

def get_val_from_file(config_file, sec, opt):
    """
        a quick way to obtain an option from a config file
    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    return get_val(config, sec, opt)


# a few quick access functions using get_val_from_file
def get_protocol(config_file):
    return get_val_from_file(config_file, "dram_structure", "protocol")


def get_ddr_speed(config_file):
    t_ck = get_val_from_file(config_file, "timing", "tCK")
    freq = int(1/t_ck * 2 * 1000.)  # to get to MHz
    freq_lookup = [800, 1333, 1600, 1866, 2133, 2400, 2666, 2933, 3200]
    actual_freq = sys.maxint
    for f in freq_lookup:
        freq_diff = abs(actual_freq - f)
        if abs(f - freq) < freq_diff:
            actual_freq = f
    return actual_freq


def get_page_size(config_file):
    """ 
        get page size in bytes
    """
    cols = get_val_from_file(config_file, "dram_structure", "columns")
    width = get_val_from_file(config_file, "dram_structure", "device_width")
    page_size = cols * width / 8
    return page_size


def get_density(config_file):
    """
        get device density in mega bytes
    """
    bankgroups = get_val_from_file(config_file, "dram_structure", "bankgroups")
    banks = get_val_from_file(config_file, "dram_structure", "banks_per_group")
    rows = get_val_from_file(config_file, "dram_structure", "rows")
    page_size = get_page_size(config_file)
    density = bankgroups * banks * rows * page_size
    return density / 1024 / 1024


def get_dict(config_file):
    """
    read a ini file specified by config_file and
    return a dict of configs with [section][option] : value structure
    """
    _config_dict = {}
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    for sec in config.sections():
        _config_dict[sec] = {}
        for opt in config.options(sec):
            _config_dict[sec][opt] = get_val(config, sec, opt)
    return _config_dict


def sub_options(config_file, sec, opt, new_value, inplace=False):
    """
        given a config file, replace the specified section, option
        with a new value, and the inplace flag decides whether the 
        config_file will be written or a tempfile handler will be 
        returned, NOTE if inplace is true all the comments in the
        original file will be gone..
    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    if not config.has_section(sec):
        config.add_section(sec)
    
    try:
        config.set(sec, opt, str(new_value))
    except ConfigParser.Error:
        print "cannot set sec:%s, option:%s, to %s" % (sec, opt, new_value)
        raise
    if not inplace:
        temp_fp = tempfile.NamedTemporaryFile()
        config.write(temp_fp)
        temp_fp.seek(0)
        return temp_fp 
    else:
        with open(config_file, "wb") as fp:
            config.write(fp)

