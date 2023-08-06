import logging
logging.basicConfig(level=logging.INFO)

from sigprocge.cl import create_opencl_context

def main():
    logging.info(create_opencl_context())

if __name__ == '__main__':
    main()

# vim:sw=4:sts=4:et
