import docker
import time

def killandAdd(name, what):
    shstr = ''
    if name.startswith("2018summer_"):
        shstr = 'su ubuntu '
    shstr += 'sh -c "'

    if what == 'gnome-panel':
        tar = 'gnome-panel'
    elif what == 'nemo' or what == 'nautilus':
        if name.startswith("dockercompose_"):
            tar = 'nemo'
        else:
            tar = 'pcmanfm'
    else:
        raise TypeError

    return [shstr + 'pkill ' + what + '"',
            shstr + 'DISPLAY=:0 ' + tar + ' > /dev/null 2>&1 &"']

def getconts():
    conts = docker.from_env().containers.list()
    newconts = []
    for cont in conts:
        if cont.name.startswith("dockercompose_") or \
           cont.name.startswith("2018summer_"):
            newconts.append(cont)
    return newconts

def main():
    conts = getconts()
    for cont in conts:
        name = cont.name 
        top = cont.top(ps_args='-A -o pid,pcpu,rss,time,command')
        scripts = []
        for p in top['Processes']:
            if float(p[1]) < 5:
                continue
            for cmd in ['gnome-panel', 'nemo', 'nautilus']:
                if cmd  in p[-1]:
                    print(p)
                    scripts.extend(killandAdd(name, cmd))

        if scripts:
            print(name)
            print(scripts)
            for s in scripts:
                cont.exec_run(s)

while True:
    time.sleep(10)
    main()
    time.sleep(3600)


# real code
"""
b.exec_run('sh -c "pkill nemo"')
b.exec_run('sh -c "DISPLAY=:0  nemo > /dev/null 2>&1 &"')
b.exec_run('sh -c "pkill gnome-panel"')
b.exec_run('sh -c "DISPLAY=:0  gnome-panel > /dev/null 2>&1 &"')

b.exec_run('su ubuntu sh -c "pkill gnome-panel"')
b.exec_run('su ubuntu sh -c "DISPLAY=:0  gnome-panel > /dev/null 2>&1 &"')
b.exec_run('su ubuntu sh -c "pkill pcmanfm"')
b.exec_run('su ubuntu sh -c "DISPLAY=:0  pcmanfm . > /dev/null 2>&1 &"')
"""
