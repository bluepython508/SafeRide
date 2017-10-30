from openalpr import Alpr


class AlprError(Exception):
    pass

def main():
    alpr = Alpr('eu', '/etc/openalpr/openalpr.conf', '/usr/share/openalpr/runtime_data')
    if not alpr.is_loaded():
        raise AlprError('Couldn\'t load OpenALPR.')



if __name__ == "__main__":
    main()
