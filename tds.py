import datetime
from time import sleep


def purge(gpib, time = 0.1):
    timeout = gpib.timeout
    gpib.set_timeout(time)
    try:
        _ = gpib.read()
    except:
        pass
    gpib.set_timeout(timeout)

def read_all(gpib, query):
    #purge(gpib)
    sleep(0.1)
    line = gpib.query(query)
    try:
        while "\n" not in line:
            sleep(0.1)
            line += gpib.read()
    except Exception as e:
        print(e)
        pass
    return line


def setup_read(gpib, queries):
    gpib.write("DATa:ENCdg ascii")
    meta = []
    for query in queries:
        line = read_all(gpib, query)
        meta.append(line)
    return ";".join(meta)


def meta_to_dict(meta):
    entries = meta.strip().split(";")
    d = []
    for line in entries:
        line_split = line.strip().split(' ')
        if len(line_split) != 0:
            d.append((line_split[0], ' '.join(line_split[1:])))
    return dict(d)


def setup_meta_header(meta, description):
    now = datetime.datetime.now()
    d = meta_to_dict(meta)
    d["Time"] = now.time().isoformat()
    d["Date"] = now.date().isoformat()
    d["Description"] = description
    return d


def save_data_file(meta, data, name):
    with open(name, 'w') as f:
        for key, value in sorted(meta.items()):
            f.write(f"#{key}: {value}\n")

        f.write("\n".join(str(pt) for pt in data))
