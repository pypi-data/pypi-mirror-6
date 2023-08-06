import sys
import os.path
from demoize import Demo, DemoServer

if __name__ == "__main__":
    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                "test/sample_code.py"))
    if sys.argv[1] == "server":
        d = DemoServer()
        d.start_server(filepath, title="My Code", heading="My Code!")
    elif sys.argv[1] == "demo":
        coords = {'w': 700, 'h': 800, 'x': 150, 'y': 0}
        d = Demo(filepath, extra_globals={'MY_CONST': 'lol'}, coords=coords,
                 sleep=0.75)
        d.run()
