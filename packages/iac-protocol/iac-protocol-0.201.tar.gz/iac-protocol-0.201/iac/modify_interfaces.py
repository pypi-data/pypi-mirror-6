import os
_ROOT = os.path.abspath(os.path.dirname(__file__))
print("Path:", os.path.join(_ROOT, 'interfaces.py'))

def modify(application_name, uncomment=True):
    new_interfaces = []
    with open(os.path.join(_ROOT, 'interfaces.py'),'r') as f:
        for line in f:
            if application_name in line and uncomment:
                new_interfaces.append(line.replace('#', ''))
            elif application_name in line and not uncomment:
                new_interfaces.append("#" + line)
            else:
                new_interfaces.append(line)
    with open(os.path.join(_ROOT, 'interfaces.py'),'w') as f:
        for line in new_interfaces:
            f.write(line)
