def ReadHeader(line):
    split = line.strip().strip("#").split(";")
    entries = dict()
    for entry in split:
        pt_space_divide = entry.split(" ")
        key = pt_space_divide[0]
        value = " ".join([pt.strip() for pt in pt_space_divide[1:]])
        entries[key] = value
    return entries

def GetTimes(incriment, zero, points):
    return [pt*incriment - zero for pt in range(int(points))]

def TransformYValues(ymult, yoffset, yzero, yvalues):
    return [(pt - yoffset)*ymult - yzero for pt in yvalues]

def TransformFile(fname):
    with open(fname, 'r') as f:
        entries = ReadHeader(f.readline())
        yvalues = list()
        for line in f:
            if len(line.strip()):
                yvalues.append(int(line))
    times = [1e9 * pt for pt in GetTimes(float(entries["XINCR"]), float(entries["XZERO"]), float(entries["NR_PT"]))]
    adj_values = TransformYValues(float(entries["YMULT"]), float(entries["YOFF"]), float(entries["YZERO"]), yvalues)
    with open(".".join(fname.strip().split(".")[:-1]) + "Adj.csv", "w") as f:
        for x, y in zip(times, adj_values):
            f.write("{},{}\n".format(x, y))

if __name__ == "__main__":
    TransformFile("Trigger_Signal_TDS744ACh1.txt")
    TransformFile("Trigger_Signal_TDS744ACh2.txt")
