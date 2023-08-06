from pandas.io.parsers import read_csv
import numpy 
import re

def determineSeparatorAndColumnCount(s, newlines):
    num_newlines = min(10, int(len(newlines)/2)-1)
    start = int(len(newlines) / 2)
    end = int(len(newlines) / 2) + num_newlines 
    if num_newlines > 1:
        s = s[newlines[start]:newlines[end]]
    characters = ['","', '"\t"', '" "', ",", "\t", " "]
    counts = [s.count(char) for char in characters]    
    candidates = [(c % num_newlines == 0) & (c != 0) for c in counts]
    candidate = candidates.index(True)
    return {"sep": characters[candidate], 
            "num_col": int(counts[candidate] / num_newlines) + 1}

def read_auto(fileName, inferOnly=False, verbose=True):
    with open(fileName) as f:
        s = f.read(10000)
    newlines = [m.start() for m in re.finditer("\n", s)]    
    info = determineSeparatorAndColumnCount(s, newlines)
    info['filepath_or_buffer'] = fileName
    info['skiprows'] = determineNSkipLines(s, newlines, info) 
    if info['sep'][0] == '"':
        info['quotechar'] = '"'
        info['sep'] = re.sub('"',"",info['sep'])
    #skippedS = numpy.loadtxt(fileName, delimiter=info['sep'], skiprows=info['skiprows'], 
    #                         dtype=str)
    # skippedS = []
    # with open(fileName) as f:
    #     for i in range(info['skiprows']):
    #         null = f.readline()
    #         print i
    #     for line in f:
    #         skippedS.append(line.strip().split(info['sep']))
    skippedN = read_csv(fileName, sep=info['sep'], skiprows=info['skiprows'], 
                             dtype=str, header=None)
    #skippedN = [x.strip().split(info['sep']) for x in s.split("\n")]
    #del skippedN[len(skippedN)-1]
    #return 1 
    info['names'] = determineHeader(skippedN, newlines, info)
    if inferOnly:
        del info['num_col']
        if info['names'] is None: 
            info['header'] = None
            del info['names']
        else:
            del info['names']
        if verbose:
            print info            
        return info
    if verbose:
        print skippedN    
    if info['names'] is not None: 
        del info['names'], info['num_col']
        return read_csv(**info)
        #skippedN.columns = skippedN.ix[0,:]
        #skippedN = skippedN.ix[1:,:] 
    return skippedN

def determineNSkipLines(s, newlines, info): 
    reg = "^([^" + info['sep'] + "\n]+" + info['sep'] + "){" + str(info['num_col']-1) + "}[^" + info['sep'] + "\n]+" 
    if re.search(reg,s[: newlines[0] - 1]):
        return 0
    for i in range(len(newlines)-1): 
        if re.search(reg, s[newlines[i] + 1:newlines[i+1] - 1]): 
            return i+1
    return 0    


def determineHeader(skippedS, newlines, info):
  strike = 0 
  if all([cannotBeFloat(x) for x in skippedS.ix[0]]): 
    if not(all([cannotBeFloat(x) for x in skippedS.ix[1]])): 
      strike += 1 
    else: 
      if all([numpy.sum(skippedS.ix[0,x] == skippedS.ix[:,x]) == 1 for x in range(len(skippedS.ix[0]))]): 
        return None
  else:
    if all(skippedS.ix[0,:] == sorted(skippedS.ix[0,:])):      
      strike += 1           
  if strike > 0:
    return skippedS.ix[0,:]

def cannotBeFloat(x):
    try:
        if isinstance(float(x), float):
            return False
    except ValueError:    
        return True

